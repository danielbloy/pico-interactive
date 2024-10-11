# Passing params, json etc:
#   https://docs.circuitpython.org/projects/httpserver/en/latest/examples.html#form-data-parsing
#   https://docs.circuitpython.org/projects/httpserver/en/latest/examples.html#url-parameters-and-wildcards
#
# URL parameters:
#   https://docs.circuitpython.org/projects/httpserver/en/latest/examples.html#url-parameters-and-wildcards
#
# Templating of results:
#   https://docs.circuitpython.org/projects/httpserver/en/latest/examples.html#templates
#
from random import randint

from adafruit_httpserver import Route, GET, Server, REQUEST_HANDLED_RESPONSE_SENT, FileResponse, Response, JSONResponse, \
    POST, Request, NOT_FOUND_404

from interactive import configuration
from interactive.configuration import NODE_COORDINATOR
from interactive.control import NETWORK_PORT_MICROCONTROLLER, NETWORK_PORT_DESKTOP
from interactive.environment import is_running_on_microcontroller, is_running_on_desktop, is_running_in_ci
from interactive.log import error
from interactive.polyfills.cpu import info as cpu_info
from interactive.polyfills.cpu import restart as cpu_restart
from interactive.polyfills.led import onboard_led
from interactive.polyfills.network import requests
from interactive.runner import Runner
from polyfills.network import get_ip

# TODO: Implement Inspect

# collections.abc is not available in CircuitPython.
if is_running_on_desktop():
    from collections.abc import Callable

NO = "NO"
YES = "YES"
OK = "OK"
ON = "ON"
OFF = "OFF"
TRIGGERED = "TRIGGERED"

HEADER_NAME = 'name'  # Name of the sender.
HEADER_ROLE = 'role'  # Role of the sender.

HEADERS = {
    HEADER_NAME: configuration.NODE_NAME,
    HEADER_ROLE: configuration.NODE_ROLE,
}


# TODO: Write tests. Also note that in CI this could be an issue in testing the JSON results
def get_port() -> int:
    if is_running_in_ci():
        return randint(5001, 50000)
    elif is_running_on_microcontroller():
        return NETWORK_PORT_MICROCONTROLLER
    else:
        return NETWORK_PORT_DESKTOP


# TODO: Write tests?
def get_host():
    if is_running_in_ci():
        return "127.0.0.1"
    else:
        return get_ip()


# TODO: Write tests?
def get_address() -> str:
    return f"{get_host()}:{get_port()}"


class NetworkController:
    """
    NetworkController provides a simple abstracted method for sending and responding to
    network messages that can be used in both CircuitPython and play old Python.

    NetworkController has built in support for the basic set of messages that every
    network connected node needs to be able to respond to.

    Please note that running a network stack on a CircuitPython board uses a lot of RAM
    so limits how much else a node can do. On a Pico, running the Pico W variant of
    CircuitPython will consume around an extra 40Kb of RAM compared to the non-W variant
    even if you are not using the networking functionality. This is unlikely to be an
    issue on a Pico 2 but on the original Pico it can cause issues.

    Instances of this class will need to register() with a Runner in order to work.
    """

    def __init__(self, server, trigger_callback: Callable[[], None] = None):

        if server is None:
            raise ValueError("server cannot be None")

        if not isinstance(server, Server):
            raise ValueError("server must be of type Server")

        if trigger_callback is not None:
            if not callable(trigger_callback):
                raise ValueError("trigger_callback must be Callable")

        self.__runner = None

        self.server = server
        self.trigger_callback = trigger_callback

        server.headers = HEADERS

        # Setup standard handlers for built-in messages.
        server.add_routes(self.get_routes())

        server.socket_timeout = 1
        if server.stopped:
            server.start(host=get_host(), port=get_port())

    def get_routes(self) -> [Route]:
        """
        The built-in routes supported by the NetworkController.
        """
        return [
            # General service routes.
            Route("/", GET, index),
            Route("/index.html", GET, index),
            Route("/cpu-information", GET, cpu_information, append_slash=True),
            Route("/inspect", GET, inspect, append_slash=True),
            Route("/restart", GET, restart, append_slash=True),
            Route("/alive", GET, alive, append_slash=True),
            Route("/name", GET, name, append_slash=True),
            Route("/role", GET, role, append_slash=True),
            Route("/details", GET, details, append_slash=True),
            Route("/blink", GET, led_blink, append_slash=True),
            Route("/led/blink", GET, led_blink, append_slash=True),
            Route("/led/<state>", [GET, POST], led_state, append_slash=True),
            # Trigger route that will call a user specified callback.
            Route("/trigger", GET, self.__trigger, append_slash=True),
        ]

    def register(self, runner: Runner) -> None:
        """
        Registers this NetworkController instance as a task with the provided Runner.
        """
        self.__runner = runner
        runner.add_loop_task(self.__serve_requests)

    async def __serve_requests(self) -> None:
        """
        The internal loop checks for incoming requests to serve.
        It also performs all shutdown tasks that need to happen
        when cancellation occurs. As well as shutting down the
        server, it unregisters with the coordinator.
        """
        if self.__runner.cancel:
            if not self.server.stopped:
                self.server.stop()

            return

        try:
            # Process any waiting requests
            pool_result = self.server.poll()

            if pool_result == REQUEST_HANDLED_RESPONSE_SENT:
                # Do something only after handling a request
                pass

        except OSError as err:
            # Because on Windows we get annoying BlockingIOErrors when running the network,
            # we swallow those here as they make all other output difficult to see.
            ignore = is_running_on_desktop() and type(err) is BlockingIOError
            if not ignore:
                error(str(err))

    def __trigger(self, request: Request):
        """
        Call the trigger method if one is specified.
        """
        return trigger(request, self.trigger_callback)


def send_message(path: str, host: str = NODE_COORDINATOR,
                 protocol: str = "http", method="GET",
                 data=None, json=None) -> Response:
    """
    Sends a message with the provided payload to the specified node, ensuring headers are included.
    """
    return requests.request(method, f"{protocol}://{host}/{path}", headers=HEADERS, data=data, json=json)


###########################################################
# ***** G E N E R A L    S E R V I C E    R O U T E S *****
###########################################################
def index(request: Request):
    """
    Serves the file html/index.html.
    """
    if request.method == GET:
        return FileResponse(request, "index.html", 'interactive/html')

    return Response(request, NO, status=NOT_FOUND_404)


def cpu_information(request: Request):
    """
    Return the current CPU temperature, frequency, voltage, RAM and various
    other information items as JSON.
    """
    if request.method == GET:
        return JSONResponse(request, cpu_info())

    return Response(request, NO, status=NOT_FOUND_404)


def inspect(request: Request):
    """
    Return a web page of information about this node.
    """
    # TODO: Implement
    if request.method == GET:
        return Response(request, "TODO inspect")

    return Response(request, NO, status=NOT_FOUND_404)


def restart(request: Request):
    """
    Restarts the microcontroller; does nothing on desktop.
    """
    if request.method != GET:
        return Response(request, NO, status=NOT_FOUND_404)

    import asyncio

    async def restart_node(seconds):
        await asyncio.sleep(seconds)
        cpu_restart()

    asyncio.create_task(restart_node(5))
    return Response(request, YES)


def alive(request: Request):
    """
    Simply returns YES in response to an alive message.
    """
    if request.method == GET:
        return Response(request, YES)

    return Response(request, NO, status=NOT_FOUND_404)


def name(request: Request):
    """
    Returns the name of the node.
    """
    if request.method == GET:
        return Response(request, configuration.NODE_NAME)

    return Response(request, NO, status=NOT_FOUND_404)


def role(request: Request):
    """
    Returns the role of the node.
    """
    if request.method == GET:
        return Response(request, configuration.NODE_ROLE)

    return Response(request, NO, status=NOT_FOUND_404)


def details(request: Request):
    """
    Returns details of the node as JSON.
    """
    if request.method == GET:
        return JSONResponse(request, configuration.details())

    return Response(request, NO, status=NOT_FOUND_404)


def led_blink(request: Request):
    """
    Blinks the local LED.
    """
    if request.method == GET:
        return Response(request, receive_blink_message(request))

    return Response(request, NO, status=NOT_FOUND_404)


def led_state(request: Request, state: str):
    """
    Turns the LED ON or OFF.
    """
    if request.method == GET:
        return Response(request, receive_led_message(request, state.upper()))

    return Response(request, NO, status=NOT_FOUND_404)


def trigger(request: Request, trigger_callback: Callable[[], None]):
    """
    Calls the trigger
    """
    if request.method == GET:
        if trigger_callback:
            trigger_callback()
            return Response(request, TRIGGERED)
        else:
            return Response(request, NO)

    return Response(request, NO, status=NOT_FOUND_404)


###############################################################
# ***** G E N E R A L    S E R V I C E    M E S S A G E S *****
###############################################################

onboard_led = onboard_led()


def receive_blink_message(request: Request) -> str:
    """
    Simply blinks the onboard LED.
    """
    import asyncio

    async def blink_led():
        onboard_led.value = not onboard_led.value
        await asyncio.sleep(0.25)
        onboard_led.value = not onboard_led.value

    asyncio.create_task(blink_led())

    return 'LED has blinked'


def receive_led_message(request: Request, state: str) -> str:
    """
    Simply turns the onboard LED either on or off.
    """
    if state == ON:
        onboard_led.value = True
    elif state == OFF:
        onboard_led.value = False
    else:
        return f'{state} is unknown'

    return f'LED is {state}'
