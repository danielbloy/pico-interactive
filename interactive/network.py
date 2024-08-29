from adafruit_httpserver import Route, GET, Server, REQUEST_HANDLED_RESPONSE_SENT, FileResponse, Response, JSONResponse, \
    POST, PUT, Request

import interactive.polyfills.cpu as cpu
from interactive import configuration
from interactive.configuration import NODE_COORDINATOR
from interactive.control import NETWORK_PORT_MICROCONTROLLER, NETWORK_PORT_DESKTOP, NETWORK_HOST_DESKTOP, \
    NETWORK_HEARTBEAT_FREQUENCY
from interactive.environment import is_running_on_microcontroller
from interactive.log import error, debug, info
from interactive.runner import Runner
from interactive.scheduler import new_scheduled_task, terminate_on_cancel

# Passing params, json etc:
#   https://teamcity.featurespace.net/buildConfiguration/AricV3_Components_AricUiClient/13633316?hideTestsFromDependencies=false
#
# URL parameters:
#   https://docs.circuitpython.org/projects/httpserver/en/latest/examples.html#url-parameters-and-wildcards
#
# Templating of results:
#   https://teamcity.featurespace.net/buildConfiguration/AricV3_Components_AricUiClient/13633316?hideTestsFromDependencies=false
#


NO = "NO"
YES = "YES"

HEADER_NAME = 'Name'  # Name of the sender.
HEADER_ROLE = 'Role'  # Role of the sender.


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

    def __init__(self, server):

        if server is None:
            raise ValueError("server cannot be None")

        if not isinstance(server, Server):
            raise ValueError("server must be of type Server")

        self.__runner = None
        self.__requires_register_with_coordinator = NODE_COORDINATOR is not None
        self.__requires_unregister_from_coordinator = NODE_COORDINATOR is not None

        self.server = server

        server.headers = {
            HEADER_NAME: configuration.NODE_NAME,
            HEADER_ROLE: configuration.NODE_ROLE,
        }

        # Setup standard handlers for built-in messages.
        server.add_routes([
            Route("/", GET, index),
            Route("/index.html", GET, index),
            Route("/cpu-information", GET, cpu_information, append_slash=True),
            Route("/inspect", GET, inspect, append_slash=True),
            Route("/register", [GET, POST], register, append_slash=True),
            Route("/unregister", [GET, POST], unregister, append_slash=True),
            Route("/heartbeat", [GET, POST], heartbeat, append_slash=True),
            Route("/restart", GET, restart, append_slash=True),
            Route("/alive", GET, alive, append_slash=True),
            Route("/name", GET, name, append_slash=True),
            Route("/role", GET, role, append_slash=True),
            Route("/blink", GET, blink, append_slash=True),
            # TODO: Led on and off: Use URL parameters
            # TODO: Lookup: Use query parameter? This should be added as an additional vocabulary.
        ])

        server.socket_timeout = 1
        if server.stopped:
            if is_running_on_microcontroller():
                server.start(port=NETWORK_PORT_MICROCONTROLLER)
            else:
                server.start(host=NETWORK_HOST_DESKTOP, port=NETWORK_PORT_DESKTOP)

    async def send_message(self, node=None):
        """
        Sends a message with the provided payload to the specified node.
        If no node is specified then the message is sent to the coordinator.
        """
        # TODO: Implement
        pass

    def add_message_handler(self):
        """
        Registers a message handler
        """
        # TODO: Implement
        pass

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

        scheduled_task = (
            new_scheduled_task(
                self.__heartbeat,
                terminate_on_cancel(self.__runner),
                NETWORK_HEARTBEAT_FREQUENCY))
        runner.add_task(scheduled_task)

    async def __serve_requests(self) -> None:
        """
        The internal loop checks for incoming requests to serve.
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
            error(str(err))

    async def __heartbeat(self) -> None:
        """
        Handles registering and unregistering from a coordinator as well as sending
        the regular heartbeat messages.
        """
        if self.__runner.cancel:
            await self.__unregister_from_coordinator()
            return

        await self.__register_with_coordinator()

        # TODO: send heartbeat message.
        # TODO: test register and unregister are sent immediately.
        # TODO: Validate Ultrasonic still works now we have changed it from registering as a loop task.

    async def __register_with_coordinator(self):
        """
        Registers this node with the controller node.
        """
        if not self.__requires_register_with_coordinator:
            debug("Nodes does not require registration, ignoring.")
            return

        # TODO: Implement
        info("Registering node with coordinator...")
        self.__requires_register_with_coordinator = False

    async def __unregister_from_coordinator(self):
        """
        Unregisters this node from the controller node.
        """
        if not self.__requires_unregister_from_coordinator:
            debug("Nodes does not require un-registration, ignoring.")
            return

        # TODO: Implement
        info("Un-registering node from coordinator...")
        self.__requires_unregister_from_coordinator = False


####################################
# ***** H T T P    R O U T E S *****
####################################
def index(request: Request):
    """
    Serves the file html/index.html.
    """
    return FileResponse(request, "index.html", 'interactive/html')


def cpu_information(request: Request):
    """
    Return the current CPU temperature, frequency, voltage, RAM and various
    other information items as JSON.
    """
    return JSONResponse(request, cpu.info())


def inspect(request: Request):
    """
    Return a web page of information about this node.
    """
    # TODO: Implement
    return Response(request, "TODO inspect")


def register(request: Request):
    """
    GET: Register this node with the coordinator.
    POST: Another node wants to register with us.
    """
    # TODO: Implement
    if request.method == GET:
        return Response(request, "TODO register self with coordinator")

    if request.method in [POST, PUT]:
        return Response(request, "TODO registered")


def unregister(request: Request):
    """
    GET: Unregister this node from the coordinator.
    POST: Another node wants to unregister from us.
    """
    # TODO: Implement
    if request.method == GET:
        return Response(request, "TODO unregister self from coordinator")

    if request.method in [POST, PUT]:
        return Response(request, "TODO unregistered")


def heartbeat(request: Request):
    """
    GET: Sends a heartbeat message from this node to the coordinator.
    POST: Another node has sent a heartbeat message to us.
    """
    # TODO: Implement
    if request.method == GET:
        return Response(request, "TODO send heartbeat message to coordinator")

    if request.method in [POST, PUT]:
        return Response(request, "TODO heartbeat message received from node")


def restart(request: Request):
    """
    Restarts the microcontroller; does nothing on desktop.
    """
    import asyncio

    async def restart_node(seconds):
        await asyncio.sleep(seconds)
        cpu.restart()

    asyncio.create_task(restart_node(5))
    return Response(request, YES)


def alive(request: Request):
    """
    Simply returns YES in response to an alive message.
    """
    return Response(request, YES)


def name(request: Request):
    """
    Returns the name of the node.
    """
    return Response(request, configuration.NODE_NAME)


def role(request: Request):
    """
    Returns the role of the node.
    """
    return Response(request, configuration.NODE_ROLE)


def blink(request: Request):
    """
    Blinks the local LED.
    """
    # TODO: Implement blink of onboard LED.
    return Response(request, 'LED has BLINKED')
