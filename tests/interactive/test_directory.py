from collections.abc import Callable, Awaitable

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
        
        """
        assert False

    def test_register_endpoint(self) -> None:
        """
        Validates that an endpoint can be registered and then looked up.
        """
        assert False

    def test_register_endpoint_multiple_times(self) -> None:
        assert False

    def test_unregister_unknown_endpoint(self) -> None:
        assert False

    def test_unregister_endpoint(self) -> None:
        assert False

    def test_unregister_endpoint_multiple_times(self) -> None:
        assert False

    def test_endpoint_expires(self) -> None:
        assert False

    def test_heartbeat_endpoint(self) -> None:
        assert False

    def test_lookup_all_endpoints(self) -> None:
        assert False

    def test_lookup_endpoint_by_name(self) -> None:
        assert False

    def test_lookup_endpoints_by_role(self) -> None:
        assert False
