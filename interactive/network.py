# TODO: Add network to Interactive
from interactive.runner import Runner


# TODO: All messages as JSON
# TODO: Receive<msg>: Handler for receiving message
# TODO: Send<msg>: Send message, if no node specified, send to coordinator
# TODO: Heartbeat message
# TODO: Blink messages
# TODO: Inspect/Status message
# TODO: Reset and other standard messages.


class NetworkController:
    """
    TODO
    """

    def __init__(self, server):
        pass
        # TODO: Setup standard handlers for built-in messages.
        # Connect to network: This is done automatically by polyfills/network.py
        # TODO: Setup a server
        # TODO: Register with coordinator.
        ## TODO: Register with coordinator here or later?

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
        TODO
        """
        # TODO: Setup loop to periodically send a heartbeat message to the coordinator.
        pass
