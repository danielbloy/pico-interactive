from adafruit_httpserver import Route, GET, Server, REQUEST_HANDLED_RESPONSE_SENT, FileResponse, Response, JSONResponse, \
    POST, PUT, Request

import interactive.polyfills.cpu as cpu
from interactive import configuration
from interactive.configuration import NODE_COORDINATOR
from interactive.control import NETWORK_PORT_MICROCONTROLLER, NETWORK_PORT_DESKTOP, NETWORK_HOST_DESKTOP
from interactive.environment import is_running_on_microcontroller
from interactive.log import error
from interactive.runner import Runner

# Passing params, json etc:
#   https://teamcity.featurespace.net/buildConfiguration/AricV3_Components_AricUiClient/13633316?hideTestsFromDependencies=false
#
# URL parameters:
#   https://docs.circuitpython.org/projects/httpserver/en/latest/examples.html#url-parameters-and-wildcards
#
# Templating of results:
#   https://teamcity.featurespace.net/buildConfiguration/AricV3_Components_AricUiClient/13633316?hideTestsFromDependencies=false
#


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
        self.__requires_registration_with_coordinator == NODE_COORDINATOR is not None
        self.__requires_unregistration_from_coordinator == NODE_COORDINATOR is not None

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
            # TODO Route("/heartbeat", [GET, POST], heartbeat, append_slash=True),
            Route("/restart", GET, restart, append_slash=True),
            Route("/alive", GET, alive, append_slash=True),
            Route("/name", GET, name, append_slash=True),
            Route("/role", GET, role, append_slash=True),
            # TODO Route("/blink", GET, blink, append_slash=True),
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

        :param runner: the runner to register with.
        """
        # TODO: Setup loop to periodically send a heartbeat message to the coordinator.
        self.__runner = runner
        runner.add_loop_task(self.__loop)

        async def heartbeat() -> None:
            """
            """
            if not self.__runner.cancel:

        self.__runner = runner
        scheduled_task = (
            new_scheduled_task(
                handler,
                terminate_on_cancel(self.__runner),
                self.__sample_frequency))
        runner.add_loop_task(scheduled_task)


    async def __loop(self):
        """
        The internal loop checks for incoming requests as well as registering and
        unregistering from a coordinator.
        """
        if self.__runner.cancel:
            if not self.server.stopped:
                self.server.stop()

            await self.__unregister_from_coordinator()

            return

        try:
            await self.__register_with_coordinator()

            # Process any waiting requests
            pool_result = self.server.poll()

            if pool_result == REQUEST_HANDLED_RESPONSE_SENT:
                # Do something only after handling a request
                pass

        except OSError as err:
            error(str(err))

    async def __register_with_coordinator(self):
        """
        Registers this node with the controller node.
        """
        if not self.__requires_registration_with_coordinator:
            return

        # TODO: Implement
        self.__requires_registration_with_coordinator = False

    async def __unregister_from_coordinator(self):
        """
        Unregisters this node from the controller node.
        """
        if not self.__requires_unregistration_from_coordinator:
            return

        # TODO: Implement
        self.__requires_unregistration_from_coordinator = False


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
    return Response(request, "TODO inspect")


def register(request: Request):
    """
    GET: Register this node with the coordinator.
    POST: Another node wants to register with us.
    """
    if request.method == GET:
        return Response(request, "TODO register self with coordinator")

    if request.method in [POST, PUT]:
        return Response(request, "TODO registered")


def unregister(request: Request):
    """
    GET: Unregister this node from the coordinator.
    POST: Another node wants to unregister from us.
    """
    if request.method == GET:
        return Response(request, "TODO unregister self from coordinator")

    if request.method in [POST, PUT]:
        return Response(request, "TODO unregistered")


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
