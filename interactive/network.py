# TODO: Add network to Interactive
from adafruit_httpserver import Request, Response, Route, GET, Server, REQUEST_HANDLED_RESPONSE_SENT

from interactive.environment import is_running_on_microcontroller
from interactive.log import error
from interactive.runner import Runner

# TODO: All messages as JSON
# TODO: Receive<msg>: Handler for receiving message
# TODO: Send<msg>: Send message, if no node specified, send to coordinator
# TODO: Heartbeat message
# TODO: Blink messages
# TODO: Inspect/Status message
# TODO: Reset and other standard messages.

HEADER_SENDER = 'Sender'  # Address of sender sending the message.
HEADER_HOST = 'Host'  # Address this message is being sent to (i.e. us).
HEADER_NAME = 'Name'  # Name of the sender.
HEADER_ROLE = 'Role'  # Role of the sender.
HEADER_DATA = 'Data'  # Data from the sender.


# @server.route("/")
def base(request: Request):
    """
    Serve a default static plain text message.
    """

    return Response(request, "Hello from the CircuitPython HTTP Server!")


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
            HEADER_SENDER: 'TODO',
            HEADER_HOST: 'TODO',
            HEADER_NAME: 'TODO',
            HEADER_ROLE: 'TODO',
            HEADER_DATA: 'TODO',
        }

        # TODO: Add more routes.
        server.add_routes([
            Route("/help", GET, base),
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
            error("BOO" + str(err))
