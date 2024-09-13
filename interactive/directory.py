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

    def register_endpoint(self, ip, name, role: str):
        name = name.strip()
        if len(name) <= 0:
            return

        if name not in self._directory:
            self._directory[name] = DirectoryController.Endpoint(ip.strip(), name, role.strip())

        self._directory[name].ip = ip.strip()
        self._directory[name].role = role.strip()
        self._directory[name].expiry_time = time.monotonic() + DIRECTORY_EXPIRY_DURATION

    def unregister_endpoint(self, name):
        name = name.strip()
        if len(name) <= 0:
            return

        if name not in self._directory:
            return

        del self._directory[name]

    def heartbeat_from_endpoint(self, ip, name, role):
        self.register_endpoint(ip, name, role)

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
