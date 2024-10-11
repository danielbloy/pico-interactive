import time

from adafruit_httpserver import GET, Response, POST, Request, NOT_FOUND_404, OK_200, BAD_REQUEST_400, \
    NOT_IMPLEMENTED_501, PUT, Route

from interactive import configuration
from interactive.configuration import NODE_COORDINATOR
from interactive.control import DIRECTORY_EXPIRY_DURATION, DIRECTORY_EXPIRY_FREQUENCY, NETWORK_HEARTBEAT_FREQUENCY
from interactive.environment import is_running_on_desktop
from interactive.log import info, debug
from interactive.network import YES, NO, send_message, OK
from interactive.polyfills.network import get_ip
from interactive.runner import Runner
from interactive.scheduler import new_scheduled_task, terminate_on_cancel

# collections.abc is not available in CircuitPython.
if is_running_on_desktop():
    from collections.abc import Callable


# TODO: Implement lookup functions.
# print(request)
# print(f"METHOD ... : '{request.method}'")
# print(f"PATH ..... : '{request.path}'")
# print(f"QPARAMS .. : '{request.query_params}'")
# print(f"HTTPV .... : '{request.http_version}'")
# print(f"HEADERS .. : '{request.headers}'")
# print(f"BODY ..... : '{request.body}'")
# print(f"RAW ...... : '{request.raw_request}'")

class DirectoryController:
    """
    DirectoryController provides a mechanism for storing details about nodes
    on the network and where that information expires after a short time period.
    This class would typically be used in conjunction with DirectoryService which
    provides the networking support.
    """

    class Endpoint:
        def __init__(self, address, name, role: str):
            self.address = address
            self.name = name
            self.role = role
            self.expiry_time = 0

    def __init__(self):
        self.__runner = None
        self._directory: dict[str, DirectoryController.Endpoint] = {}

    def register(self, runner: Runner) -> None:
        """
        Registers this DirectoryController instance as a task with the provided Runner.
        We only need to run this every once in a while to check for expired names.

        """
        self.__runner = runner

        scheduled_task = (
            new_scheduled_task(
                self.__expire_endpoints,
                terminate_on_cancel(self.__runner),
                DIRECTORY_EXPIRY_FREQUENCY))

        runner.add_task(scheduled_task)

    async def __expire_endpoints(self) -> None:
        """
        Removes all registered endpoints from this DirectoryController that
        have expired.
        """
        info("Checking for endpoint expiration.")
        now = time.monotonic()
        to_remove = [name for name, endpoint in self._directory.items() if endpoint.expiry_time < now]

        for name in to_remove:
            del self._directory[name]

    def register_endpoint(self, address: str, name: str, role: str):
        """
        Registers an endpoint. The name and role information are considered case-insensitive
        so will be stored as lowercase. The name is considered the unique aspect of
        an endpoint so a single name corresponds to a single endpoint. Multiple endpoint
        names can have the same address or role.

        Where an endpoint is re-registered, the new data overwrites the old data.

        Re-registering an endpoint extends its expiry time.

        :param address: The address of the endpoint, as a string. Stored as lowercase.
        :param name: The name of the endpoint, as a string. Stored as lowercase.
        :param role: The nominal role of the registered endpoint. Stored as lowercase.
        """
        if name is None:
            return

        lookup = name.strip().lower()
        if len(lookup) <= 0:
            return

        if lookup not in self._directory:
            self._directory[lookup] = (
                DirectoryController.Endpoint(address.strip().lower(), lookup, role.strip().lower()))

        self._directory[lookup].address = address.strip().lower()
        self._directory[lookup].role = role.strip().lower()
        self._directory[lookup].expiry_time = time.monotonic() + DIRECTORY_EXPIRY_DURATION

        return

    def unregister_endpoint(self, name):
        """
        Removes an endpoint. If no endpoint exists, nothing happens.
        """
        if name is None:
            return

        lookup = name.strip().lower()
        if len(lookup) <= 0:
            return

        if lookup not in self._directory:
            return

        del self._directory[lookup]

    def heartbeat_from_endpoint(self, address, name, role):
        """
        Simply forwards to register_endpoint()
        """
        return self.register_endpoint(address, name, role)

    def lookup_all_endpoints(self) -> dict[str, str]:
        """
        Returns the address for all the known nodes.
        """
        return dict((name, endpoint.address) for name, endpoint in self._directory.items())

    def lookup_endpoint_by_name(self, name) -> [None, str]:
        """
        Returns the address for the matching name.
        """
        if name is None:
            return None

        lookup = name.strip().lower()
        if len(lookup) <= 0:
            return

        if lookup not in self._directory:
            return None

        return self._directory[lookup].address

    def lookup_endpoints_by_role(self, role) -> [None, dict[str, str]]:
        """
        Return a dictionary of names to addresses.
        """
        if role is None:
            return None

        lookup = role.strip().lower()
        if len(lookup) <= 0:
            return

        return dict((name, endpoint.address) for name, endpoint in self._directory.items() if endpoint.role == lookup)


class DirectoryService:
    """
    DirectoryService provides a simple network naming service to
    allow microcontrollers to communicate with other microcontrollers.
    The premise is that a microcontroller will register with another
    microcontroller (called a coordinator) and periodically send
    heartbeat messages to keep its name alive. Other microcontrollers
    can then query the coordinator to find the address (and other
    details) of nodes registered with the coordinator. Each node will
    have at least a name and role metadata in addition to the address.

    This class works closely with the NetworkController which handles
    all the microcontroller communication. This class handles the
    directory information including expiry of data.

    Instances of this class will need to register() with a Runner in
    order to work.
    """

    def __init__(self):
        self.__runner = None
        self.__requires_register_with_coordinator = NODE_COORDINATOR is not None
        self.__requires_unregister_from_coordinator = NODE_COORDINATOR is not None
        self.__requires_heartbeat_messages = False
        self.directory = DirectoryController()

    def get_routes(self) -> [Route]:
        """
        The built-in routes supported by the DirectoryService.
        """
        return [
            # Directory service routes
            Route("/register", [GET, POST], lambda req: register(req, self.directory), append_slash=True),
            Route("/unregister", [GET, POST], lambda req: unregister(req, self.directory), append_slash=True),
            Route("/heartbeat", [GET, POST], lambda req: heartbeat(req, self.directory), append_slash=True),
            Route("/lookup/all", GET, lambda req: lookup_all(req, self.directory), append_slash=True),
            Route("/lookup/name/<name>", GET, lambda req, n: lookup_name(req, self.directory, n), append_slash=True),
            Route("/lookup/role/<role>", GET, lambda req, r: lookup_role(req, self.directory, r), append_slash=True),
        ]

    def register(self, runner: Runner) -> None:
        """
        Registers this DirectoryService instance as a task with the provided Runner.
        Multiple separate tasks are registered with the runner.
        * One for the DirectoryController to handle detail expiration.
        * One to manage the registration of the node with a coordinator, including sending
          regular heartbeat messages.
        * One to unregister when the task is cancelled.
        """
        self.__runner = runner
        self.directory.register(runner)

        runner.add_loop_task(self.__handle_cancellation)

        # Only setup the heartbeat task if we have a coordinator.
        if NODE_COORDINATOR:
            scheduled_task = (
                new_scheduled_task(
                    self.__heartbeat,
                    terminate_on_cancel(self.__runner),
                    NETWORK_HEARTBEAT_FREQUENCY))
            runner.add_task(scheduled_task)

    async def __handle_cancellation(self) -> None:
        """
        Handles unregistering with the coordinator during shutdown.
        """
        if self.__runner.cancel:
            # This has to be done here as __heartbeat() is wrapped by
            # a task scheduler which checks for cancellation and
            # prevents client code running in such a scenario.
            await self.__unregister_from_coordinator()

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


###############################################################
# ***** D I R E C T O R Y    S E R V I C E    R O U T E S *****
###############################################################


def __standard_directory_method(
        request: Request, directory: DirectoryController,
        get_func: Callable[[str], str],
        post_func: Callable[[Request, DirectoryController], Response]):
    """
    The register, unregister and heartbeat messages all have exactly the
    same form, the only difference being the operations. This function
    wraps up the logic which validates the arguments and properties that
    are required.
    """
    if directory is None:
        raise ValueError("No directory controller specified")

    if request.method == GET:
        if NODE_COORDINATOR is None:
            raise ValueError("No coordinator configured")

        return Response(request, get_func(NODE_COORDINATOR))

    if request.method in [POST, PUT]:
        return post_func(request, directory)

    return Response(request, NO, status=NOT_FOUND_404)


def register(request: Request, directory: DirectoryController):
    """
    GET: Register this node with the coordinator. Will return an error if the
         coordinator configuration is not set.
    POST, PUT: Another node wants to register with us.
    """
    return __standard_directory_method(request, directory, send_register_message, receive_register_message)


def unregister(request: Request, directory: DirectoryController):
    """
    GET: Unregister this node from the coordinator.
    POST, PUT: Another node wants to unregister from us.
    """
    return __standard_directory_method(request, directory, send_unregister_message, receive_unregister_message)


def heartbeat(request: Request, directory: DirectoryController):
    """
    GET: Sends a heartbeat message from this node to the coordinator.
    POST, PUT: Another node has sent a heartbeat message to us.
    """
    return __standard_directory_method(request, directory, send_heartbeat_message, receive_heartbeat_message)


def lookup_all(request: Request, directory: DirectoryController):
    """
    Return all known nodes
    """
    # TODO: Implement by returning JSON.
    if request.method == GET:
        return Response(request, NO, status=NOT_IMPLEMENTED_501)

    return Response(request, NO, status=NOT_FOUND_404)


def lookup_name(request: Request, directory: DirectoryController, name: str):
    """
    Returns all known nodes by name as a JSON response in the following form:
    {
        "name": "node_name",
        "nodes": [
               "1.2.3.4",
               "a.b.c.d",
        ]
    }
    """
    if request.method != GET:
        return Response(request, NO, status=NOT_FOUND_404)

    return Response(request, NO, status=NOT_IMPLEMENTED_501)


def lookup_role(request: Request, directory: DirectoryController, role: str):
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
    """
    Sends a register message to the specified node.
    """
    info(f"Registering with {node}...")

    try:
        data = configuration.details()
        data["address"] = get_ip()
        with send_message(host=node, path='/register', json=data) as response:
            if response._status == OK_200:
                return YES
            else:
                return NO

    except:
        return NO


def receive_register_message(request: Request, directory: DirectoryController) -> Response:
    """
    Registers the details about the provided node with the given directory controller.
    The format of the expected body JSON is:
    {
        "address": "1.2.3.4:80",
        "name": "node_name",
        "role": "node_role"
    }
    """
    info("Registering node...")

    if request is None:
        raise ValueError("No request specified")

    if directory is None:
        raise ValueError("No directory controller specified")

    try:
        data = request.json()
        if "address" not in data:
            return Response(request, "NO_ADDRESS_SPECIFIED", status=BAD_REQUEST_400)

        if "name" not in data:
            return Response(request, "NO_NAME_SPECIFIED", status=BAD_REQUEST_400)

        if "role" not in data:
            return Response(request, "NO_ROLE_SPECIFIED", status=BAD_REQUEST_400)

        directory.register_endpoint(data["address"], data["name"], data["role"])
        info(f'Registered node: {data["name"]}, role: {data["role"]}, address: {data["address"]}')

    except:
        return Response(request, "FAILED_TO_PARSE_BODY", status=BAD_REQUEST_400)

    return Response(request, OK)


def send_unregister_message(node: str) -> str:
    """
    Sends an unregister message to the specified node.
    """
    info(f"Registering from {node}...")

    try:
        data = configuration.details()
        data["address"] = get_ip()
        with send_message(host=node, path='/unregister', json=data) as response:
            if response._status == OK_200:
                return YES
            else:
                return NO

    except:
        return NO


def receive_unregister_message(request: Request, directory: DirectoryController) -> Response:
    """
    Simply unregisters the node. If it does not exist, no error is thrown.
    The format of the expected body JSON is:
    {
        "name": "node_name"
    }
    """
    info("Unregistering node...")

    if request is None:
        raise ValueError("No request specified")

    if directory is None:
        raise ValueError("No directory controller specified")

    try:
        data = request.json()
        if "name" not in data:
            return Response(request, "NO_NAME_SPECIFIED", status=BAD_REQUEST_400)

        directory.unregister_endpoint(data["name"])
        info(f'unregistered node: {data["name"]}')

    except:
        return Response(request, "FAILED_TO_PARSE_BODY", status=BAD_REQUEST_400)

    return Response(request, OK)


def send_heartbeat_message(node: str) -> str:
    """
    Sends a heartbeat message to the specified node.
    """
    info(f"Heartbeat with {node}...")

    try:
        data = configuration.details()
        data["address"] = get_ip()
        with send_message(host=node, path='/heartbeat', json=data) as response:
            if response._status == OK_200:
                return YES
            else:
                return NO

    except:
        return NO


def receive_heartbeat_message(request: Request, directory: DirectoryController) -> Response:
    """
    This simply re-routes to register as it is effectively the same.

    FUTURE: We could at some future point put in an optimisation here to
            lookup whether an item has already been registered. If such
            a case, we would already have the address, name and role so
            as long as at least one of or name was registered, the other
            data would become optional.
    """
    info("Received heartbeat message...")
    return receive_register_message(request, directory)
