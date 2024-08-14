# TODO: Add network to Interactive
from urllib.request import Request

from adafruit_httpserver import Route, GET, Server, REQUEST_HANDLED_RESPONSE_SENT, FileResponse, Response, JSONResponse

from interactive import configuration
from interactive.environment import is_running_on_microcontroller
from interactive.log import error
from interactive.polyfills.cpu import cpu_info
from interactive.runner import Runner

# TODO: All messages as JSON
# TODO: Receive<msg>: Handler for receiving message
# TODO: Send<msg>: Send message, if no node specified, send to coordinator
# TODO: Heartbeat message
# TODO: Blink messages
# TODO: Inspect/Status message
# TODO: Reset and other standard messages.

HEADER_SENDER = 'Sender'  # Address of sender sending the message.
HEADER_NAME = 'Name'  # Name of the sender.
HEADER_ROLE = 'Role'  # Role of the sender.


class NetworkController:
    """
    TODO
    """

    def __init__(self, server):

        if server is None:
            raise ValueError("server cannot be None")

        if not isinstance(server, Server):
            raise ValueError("server must be of type Server")

        self.__runner = None
        self.server = server

        # TODO: Setup standard handlers for built-in messages.
        server.headers = {
            HEADER_SENDER: 'TODO',  # TODO: This is probably not needed.
            HEADER_NAME: configuration.NODE_NAME,
            HEADER_ROLE: configuration.NODE_ROLE,
        }

        server.add_routes([
            Route("/", GET, index),
            # Route("/index.html", GET, index), TODO Test
            Route("/cpu-information", GET, cpu_information, append_slash=True),
            Route("/inspect", GET, inspect, append_slash=True),
            Route("/register", GET, register, append_slash=True),
            Route("/unregister", GET, unregister, append_slash=True),
            Route("/restart", GET, restart, append_slash=True),
            Route("/alive", GET, alive, append_slash=True),
            Route("/name", GET, name, append_slash=True),
            Route("/role", GET, role, append_slash=True),
            # TODO: Blink
        ])

        server.socket_timeout = 1
        if server.stopped:
            if is_running_on_microcontroller():
                server.start(port=80)
            else:
                # TODO: Make the host and port configurable on desktop
                server.start(host="127.0.0.1", port=5001)

        # TODO: Register with coordinator.
        # TODO: Register with coordinator here or later?

    def send_message(self, node=None):
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

    def __register_with_coordinator(self):
        """
        Registers this node with the controller node.
        """
        pass
        # TODO: Implement

    def __unregister_from_coordinator(self):
        """
        Unregisters this node from the controller node.
        """
        pass
        # TODO: Implement

    def register(self, runner: Runner) -> None:
        """
        Registers this NetworkController instance as a task with the provided Runner.

        :param runner: the runner to register with.
        """
        # TODO: Setup loop to periodically send a heartbeat message to the coordinator.

        self.__runner = runner
        runner.add_loop_task(self.__loop)

    async def __loop(self):
        """
        The internal loop checks for songs in the queue and plays them if
        nothing is playing.
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


####################################
# ***** H T T P    R O U T E S *****
####################################
def index(request: Request):
    """
    Serves the file html/index.html.
    """
    return FileResponse(request, "index.html", "/html")


def cpu_information(request: Request):
    """
    Return the current CPU temperature, frequency, and voltage as JSON.
    """
    return JSONResponse(request, cpu_info())


def inspect(request: Request):
    return Response(request, "TODO")


def register(request: Request):
    return Response(request, "TODO")


def unregister(request: Request):
    return Response(request, "TODO")


def restart(request: Request):
    return Response(request, "TODO")


def alive(request: Request):
    return Response(request, "Yes")


def name(request: Request):
    return Response(request, configuration.NODE_NAME)


def role(request: Request):
    return Response(request, configuration.NODE_ROLE)
