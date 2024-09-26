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
from adafruit_httpserver import Route, GET, Server, REQUEST_HANDLED_RESPONSE_SENT, FileResponse, Response, JSONResponse, \
    POST, PUT, Request, NOT_IMPLEMENTED_501, NOT_FOUND_404

from interactive import configuration
from interactive.configuration import NODE_COORDINATOR
from interactive.control import NETWORK_PORT_MICROCONTROLLER, NETWORK_PORT_DESKTOP, NETWORK_HOST_DESKTOP, \
    NETWORK_HEARTBEAT_FREQUENCY
from interactive.environment import is_running_on_microcontroller, is_running_on_desktop
from interactive.log import error, debug, info
from interactive.polyfills.cpu import info as cpu_info
from interactive.polyfills.cpu import restart as cpu_restart
from interactive.polyfills.led import onboard_led
from interactive.polyfills.network import requests
from interactive.runner import Runner
from interactive.scheduler import new_scheduled_task, terminate_on_cancel

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
        self.__requires_register_with_coordinator = NODE_COORDINATOR is not None
        self.__requires_unregister_from_coordinator = NODE_COORDINATOR is not None
        self.__requires_heartbeat_messages = False

        self.server = server
        self.trigger_callback = trigger_callback

        server.headers = HEADERS

        # Setup standard handlers for built-in messages.
        server.add_routes([
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
            # Directory service routes
            Route("/register", [GET, POST], register, append_slash=True),
            Route("/unregister", [GET, POST], unregister, append_slash=True),
            Route("/heartbeat", [GET, POST], heartbeat, append_slash=True),
            Route("/lookup/all", GET, lookup_all, append_slash=True),
            Route("/lookup/name/<name>", GET, lookup_name, append_slash=True),
            Route("/lookup/role/<role>", GET, lookup_role, append_slash=True),
        ])

        server.socket_timeout = 1
        if server.stopped:
            if is_running_on_microcontroller():
                server.start(port=NETWORK_PORT_MICROCONTROLLER)
            else:
                server.start(host=NETWORK_HOST_DESKTOP, port=NETWORK_PORT_DESKTOP)

    def register(self, runner: Runner) -> None:
        """
        Registers this NetworkController instance as a task with the provided Runner.
        Two separate tasks are registered with the runner. One to handle network
        requests as part of the server and another to manage the registration of the
        node with a coordinator, including sending regular heartbeat messages.

        :param runner: the runner to register with.
        """
        self.__runner = runner
        runner.add_loop_task(self.__serve_requests)

        # Only setup the heartbeat task if we have a coordinator.
        if NODE_COORDINATOR:
            scheduled_task = (
                new_scheduled_task(
                    self.__heartbeat,
                    terminate_on_cancel(self.__runner),
                    NETWORK_HEARTBEAT_FREQUENCY))
            runner.add_task(scheduled_task)

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

            # This has to be done here as __heartbeat() is wrapped by
            # a task scheduler which checks for cancellation and
            # prevents client code running in such a scenario.
            await self.__unregister_from_coordinator()

            return

        try:
            # Process any waiting requests
            pool_result = self.server.poll()

            if pool_result == REQUEST_HANDLED_RESPONSE_SENT:
                # Do something only after handling a request
                pass

        except OSError as err:
            error(str(err))

    async def __heartbeat(self) -> None:
        """
        Handles registering with a coordinator as well as sending
        the regular heartbeat messages. We cannot do the unregister
        here because scheduled tasks are wrapped in a cancellation
        check. Therefore, the cancellation is checked __serve_requests()
        """
        if self.__requires_heartbeat_messages:
            send_heartbeat_message(NODE_COORDINATOR)

        await self.__register_with_coordinator()

    async def __register_with_coordinator(self):
        """
        Registers this node with the controller node.
        """
        if not self.__requires_register_with_coordinator:
            debug("Nodes does not require registration, ignoring.")
            return

        send_register_message(NODE_COORDINATOR)
        self.__requires_register_with_coordinator = False
        self.__requires_unregister_from_coordinator = True
        self.__requires_heartbeat_messages = True

    async def __unregister_from_coordinator(self):
        """
        Unregisters this node from the controller node. Also disables sending
        of any heartbeat messages.
        """
        if not self.__requires_unregister_from_coordinator:
            debug("Nodes does not require un-registration, ignoring.")
            return

        send_unregister_message(NODE_COORDINATOR)
        self.__requires_unregister_from_coordinator = False
        self.__requires_register_with_coordinator = True
        self.__requires_heartbeat_messages = False

    def __trigger(self, request: Request):
        """
        Call the trigger method if one is specified.
        """
        return trigger(request, self.trigger_callback)


def send_message(path: str, host: str = NODE_COORDINATOR,
                 protocol: str = "http", method="GET",
                 data=None, json=None):
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


###############################################################
# ***** D I R E C T O R Y    S E R V I C E    R O U T E S *****
###############################################################

def register(request: Request):
    """
    GET: Register this node with the coordinator. Will return an error if the
         coordinator configuration is not set.
    POST: Another node wants to register with us.
    """
    if NODE_COORDINATOR is None:
        raise ValueError("No coordinator configured")

    if request.method == GET:
        return Response(request, send_register_message(NODE_COORDINATOR))

    if request.method in [POST, PUT]:
        return Response(request, receive_register_message(request))

    return Response(request, NO, status=NOT_FOUND_404)


def unregister(request: Request):
    """
    GET: Unregister this node from the coordinator.
    POST: Another node wants to unregister from us.
    """
    if NODE_COORDINATOR is None:
        raise ValueError("No coordinator configured")

    if request.method == GET:
        return Response(request, send_unregister_message(NODE_COORDINATOR))

    if request.method in [POST, PUT]:
        return Response(request, receive_unregister_message(request))

    return Response(request, NO, status=NOT_FOUND_404)


def heartbeat(request: Request):
    """
    GET: Sends a heartbeat message from this node to the coordinator.
    POST: Another node has sent a heartbeat message to us.
    """
    if NODE_COORDINATOR is None:
        raise ValueError("No coordinator configured")

    if request.method == GET:
        return Response(request, send_heartbeat_message(NODE_COORDINATOR))

    if request.method in [POST, PUT]:
        return Response(request, receive_heartbeat_message(request))

    return Response(request, NO, status=NOT_FOUND_404)


def lookup_all(request: Request):
    """
    Return all known nodes
    """
    # TODO: Implement by returning JSON.
    if request.method == GET:
        return Response(request, NO, status=NOT_IMPLEMENTED_501)

    return Response(request, NO, status=NOT_FOUND_404)


def lookup_name(request: Request, name: str):
    """
    Returns all known nodes by name.
    """
    # TODO: Implement by returning JSON
    if request.method == GET:
        return Response(request, NO, status=NOT_IMPLEMENTED_501)

    return Response(request, NO, status=NOT_FOUND_404)


def lookup_role(request: Request, role: str):
    """
    Returns all known nodes by role.
    """
    # TODO: Implement by returning JSON
    if request.method == GET:
        return Response(request, NO, status=NOT_IMPLEMENTED_501)

    return Response(request, NO, status=NOT_FOUND_404)


###################################################################
# ***** D I R E C T O R Y    S E R V I C E    M E S S A G E S *****
###################################################################

def send_register_message(node: str) -> str:
    info("Registering node with coordinator...")
    # TODO
    return "registered with coordinator"


def receive_register_message(request: Request) -> str:
    info("Registering node...")
    # TODO
    return OK


def send_unregister_message(node) -> str:
    info("Unregistering node from coordinator...")
    # TODO
    # TODO: Remove the invocation of quotes
    # with send_message(protocol='https', host='www.adafruit.com', path='api/quotes.php') as response:
    #    print(response.headers)
    #    print(response.text)

    return "unregistered from coordinator"


def receive_unregister_message(request: Request) -> str:
    info("Unregistering node...")
    # TODO
    return OK


def send_heartbeat_message(node: str) -> str:
    info("Sending heartbeat message to coordinator...")
    # TODO
    return "heartbeat message sent to coordinator"


def receive_heartbeat_message(request: Request) -> str:
    info("Received heartbeat message...")
    # TODO
    return "TODO heartbeat message received from node"
