import time
from collections.abc import Callable, Awaitable

from control import DIRECTORY_EXPIRY_DURATION
from directory import DirectoryController
from interactive.runner import Runner


class TestDirectoryController:

    def test_registering_with_runner(self) -> None:
        """
        Validates the DirectoryController registers with the Runner
        """
        add_task_count: int = 0

        class TestRunner(Runner):
            def add_loop_task(self, task: Callable[[], Awaitable[None]]) -> None:
                nonlocal add_task_count
                add_task_count += 1

            def add_task(self, task: Callable[[], Awaitable[None]]) -> None:
                nonlocal add_task_count
                add_task_count += 1

        runner = TestRunner()
        controller = DirectoryController()
        assert add_task_count == 0
        controller.register(runner)
        assert add_task_count == 1
        assert len(controller.lookup_all_endpoints()) == 0

    def test_register_endpoint_fails_with_no_name(self) -> None:
        """
        Validates that an endpoint with an empty name cannot be registered.
        """
        controller = DirectoryController()
        assert len(controller.lookup_all_endpoints()) == 0
        assert not controller.register_endpoint("IP", "", "")
        assert len(controller.lookup_all_endpoints()) == 0

        assert not controller.register_endpoint("IP", "", "")
        assert len(controller.lookup_all_endpoints()) == 0

    def test_register_endpoint(self) -> None:
        """
        Validates that an endpoint can be registered and then looked up.
        This also validates the case in-sensitive nature of the lookup and
        the other stored data.
        """
        controller = DirectoryController()
        assert len(controller.lookup_all_endpoints()) == 0

        # Register the endpoint
        before = time.monotonic()
        assert controller.register_endpoint("a.b.C.D", "AlPhA", "ROLE")
        assert len(controller.lookup_all_endpoints()) == 1

        # Check the name, role and IP address are stored as lowercase
        assert "alpha" in controller._directory
        assert controller._directory["alpha"].role == "role"
        assert controller._directory["alpha"].ip == "a.b.c.d"

        # Check that the expiry time is generated correctly
        assert controller._directory["alpha"].expiry_time > before
        assert controller._directory["alpha"].expiry_time >= before + DIRECTORY_EXPIRY_DURATION

    def test_register_endpoint_multiple_times(self) -> None:
        """
        Validates that an endpoint can be registered multiple times.
        Validates that subsequent registrations overwrite previous data
        """
        controller = DirectoryController()
        assert len(controller.lookup_all_endpoints()) == 0

        # Register the endpoint and save the expiry time
        before = time.monotonic()
        assert controller.register_endpoint("a.b.c.d", "BEta", "ROLE")
        assert len(controller.lookup_all_endpoints()) == 1
        assert "beta" in controller._directory
        assert controller._directory["beta"].role == "role"
        assert controller._directory["beta"].ip == "a.b.c.d"
        original_expiry_time = controller._directory["beta"].expiry_time

        # Pause for a period before re-registering
        time.sleep(0.2)

        # Re-register with different data
        assert controller.register_endpoint("1.2.3.4", "beTA", "special")
        assert len(controller.lookup_all_endpoints()) == 1
        assert "beta" in controller._directory
        assert controller._directory["beta"].role == "special"
        assert controller._directory["beta"].ip == "1.2.3.4"
        new_expiry_time = controller._directory["beta"].expiry_time

        assert new_expiry_time > original_expiry_time

    def test_unregister_unknown_endpoint(self) -> None:
        assert False

    def test_unregister_endpoint(self) -> None:
        assert False

    def test_unregister_endpoint_multiple_times(self) -> None:
        assert False

    def test_endpoint_expires(self) -> None:
        assert False

    def test_heartbeat_endpoint(self) -> None:
        """
        Validates that the heartbeat_from_endpoint() function just forwards
        to register_endpoint().
        """
        controller = DirectoryController()
        assert len(controller.lookup_all_endpoints()) == 0

        assert controller.heartbeat_from_endpoint("a.b.C.D", "AlPhA", "ROLE")
        assert len(controller.lookup_all_endpoints()) == 1
        assert "alpha" in controller._directory
        assert controller._directory["alpha"].role == "role"
        assert controller._directory["alpha"].ip == "a.b.c.d"

    def test_lookup_all_endpoints(self) -> None:
        assert False

    def test_lookup_endpoint_by_name(self) -> None:
        assert False

    def test_lookup_endpoints_by_role(self) -> None:
        assert False
