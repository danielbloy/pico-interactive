import time

from interactive.control import DIRECTORY_EXPIRY_DURATION, DIRECTORY_EXPIRY_FREQUENCY
from interactive.log import info
from interactive.runner import Runner
from interactive.scheduler import new_scheduled_task, terminate_on_cancel


class DirectoryController:
    """
    DirectoryController provides a simple network naming service to
    allow microcontrollers to communicate with other microcontrollers.
    The premise is that a microcontroller will register with another
    microcontroller (called a coordinator) and periodically send
    heartbeat messages to keep its name alive. Other microcontrollers
    can then query the coordinator to find the IP address (and other
    details) of nodes registered with the coordinator. Each node will
    have at least a name and role metadata in addition to the IP address.

    This class works closely with the NetworkController which handles
    all the microcontroller communication. This class handles the
    directory information including expiry of data.
    """

    class Endpoint:
        def __init__(self, ip, name, role: str):
            self.ip = ip
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

    def register_endpoint(self, ip: str, name: str, role: str) -> bool:
        """
        Registers an endpoint. The name and role information are considered case-insensitive
        so will be stored as lowercase. The name is considered the unique aspect of
        an endpoint so a single name corresponds to a single endpoint. Multiple endpoint
        names can have the same IP address or role.

        Where an endpoint is re-registered, the new data overwrites the old data.

        Re-registering an endpoint extends its expiry time.

        Returns whether registration (or re-registration) was successful or not.

        :param ip:   The IP address of the endpoint, as a string. Stored as lowercase.
        :param name: The name of the endpoint, as a string. Stored as lowercase.
        :param role: The nominal role of the registered endpoint. Stored as lowercase.
        """
        lookup = name.strip().lower()
        if len(lookup) <= 0:
            return False

        if lookup not in self._directory:
            self._directory[lookup] = (
                DirectoryController.Endpoint(ip.strip().lower(), lookup, role.strip().lower()))

        self._directory[lookup].ip = ip.strip().lower()
        self._directory[lookup].role = role.strip().lower()
        self._directory[lookup].expiry_time = time.monotonic() + DIRECTORY_EXPIRY_DURATION

        return True

    def unregister_endpoint(self, name) -> bool:
        lookup = name.strip().lower()
        if len(lookup) <= 0:
            return False

        if lookup not in self._directory:
            return True

        del self._directory[lookup]

    def heartbeat_from_endpoint(self, ip, name, role) -> bool:
        """
        Simply forwards to register_endpoint()
        """
        return self.register_endpoint(ip, name, role)

    # Returns the IP address for all the known nodes
    def lookup_all_endpoints(self):
        return dict((name, endpoint.ip) for name, endpoint in self._directory.items())

    # Returns the IP address for the first matching name
    def lookup_endpoint_by_name(self, name) -> [None, str]:
        name = name.strip()

        if name not in self._directory:
            return None

        return self._directory[name].ip

    # Return a dictionary of names to IPs.
    def lookup_endpoints_by_role(self, role):
        return dict((name, endpoint.ip) for name, endpoint in self._directory.items() if endpoint.role == role)
