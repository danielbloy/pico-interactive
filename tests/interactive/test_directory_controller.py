import time
from collections.abc import Callable, Awaitable

import interactive.directory as directory
from interactive.control import DIRECTORY_EXPIRY_DURATION
from interactive.directory import DirectoryController
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

        controller.register_endpoint("ADDRESS", None, "")
        assert len(controller.lookup_all_endpoints()) == 0

        controller.register_endpoint("ADDRESS", "", "")
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
        controller.register_endpoint("a.b.C.D", "AlPhA", "ROLE")
        assert len(controller.lookup_all_endpoints()) == 1

        # Check the name, role and address are stored as lowercase
        assert "alpha" in controller._directory
        assert controller._directory["alpha"].role == "role"
        assert controller._directory["alpha"].address == "a.b.c.d"

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
        controller.register_endpoint("a.b.c.d", "BEta", "ROLE")
        assert len(controller.lookup_all_endpoints()) == 1
        assert "beta" in controller._directory
        assert controller._directory["beta"].role == "role"
        assert controller._directory["beta"].address == "a.b.c.d"
        original_expiry_time = controller._directory["beta"].expiry_time

        # Pause for a period before re-registering
        time.sleep(0.2)

        # Re-register with different data
        controller.register_endpoint("1.2.3.4", "beTA", "special")
        assert len(controller.lookup_all_endpoints()) == 1
        assert "beta" in controller._directory
        assert controller._directory["beta"].role == "special"
        assert controller._directory["beta"].address == "1.2.3.4"
        new_expiry_time = controller._directory["beta"].expiry_time

        assert new_expiry_time > original_expiry_time

    def test_unregister_unknown_endpoint(self) -> None:
        """
        Validates that removing an unknown endpoint does not error
        """
        controller = DirectoryController()
        assert len(controller.lookup_all_endpoints()) == 0

        # First try removing from an empty directory
        controller.unregister_endpoint(None)
        assert len(controller.lookup_all_endpoints()) == 0
        controller.unregister_endpoint("")
        assert len(controller.lookup_all_endpoints()) == 0
        controller.unregister_endpoint("alpha")
        assert len(controller.lookup_all_endpoints()) == 0

        # Add in an couple of entries and try removing again.
        controller.register_endpoint("1.2.3.4", "beta", "role")
        controller.register_endpoint("1.2.3.4", "gamma", "special")

        controller.unregister_endpoint(None)
        assert len(controller.lookup_all_endpoints()) == 2
        controller.unregister_endpoint("")
        assert len(controller.lookup_all_endpoints()) == 2
        controller.unregister_endpoint("alpha")
        assert len(controller.lookup_all_endpoints()) == 2

    def test_unregister_endpoint(self) -> None:
        """
        Validates that an endpoint can be unregistered.
        """
        controller = DirectoryController()
        assert len(controller.lookup_all_endpoints()) == 0

        # Add in entries.
        controller.register_endpoint("1.2.3.4", "alpha", "path")
        controller.register_endpoint("a.b.c.d", "beta", "witch")
        controller.register_endpoint("1.2.3.4", "gamma", "spiders")
        assert len(controller.lookup_all_endpoints()) == 3

        # Use all uppercase should still remove it
        controller.unregister_endpoint("ALPHA")
        assert len(controller.lookup_all_endpoints()) == 2
        assert "beta" in controller._directory
        assert "gamma" in controller._directory

        controller.unregister_endpoint("GammA")
        assert len(controller.lookup_all_endpoints()) == 1
        assert "beta" in controller._directory

        controller.unregister_endpoint("beta")
        assert len(controller.lookup_all_endpoints()) == 0

    def test_unregister_endpoint_multiple_times(self) -> None:
        """
        Validates that an unregistering an endpoint multiple times does not error.
        """
        controller = DirectoryController()
        assert len(controller.lookup_all_endpoints()) == 0

        # Add in entries.
        controller.register_endpoint("1.2.3.4", "alpha", "path")
        controller.register_endpoint("a.b.c.d", "beta", "witch")
        controller.register_endpoint("1.2.3.4", "gamma", "spiders")
        assert len(controller.lookup_all_endpoints()) == 3

        controller.unregister_endpoint("beta")
        assert len(controller.lookup_all_endpoints()) == 2
        assert "alpha" in controller._directory
        assert "gamma" in controller._directory

        controller.unregister_endpoint("beta")
        assert len(controller.lookup_all_endpoints()) == 2
        assert "alpha" in controller._directory
        assert "gamma" in controller._directory

    def test_endpoint_expires(self, monkeypatch) -> None:
        """
        Validates that an endpoint expires. To prove this we
        """
        # We need to monkey patch the frequency to check as well as the expiry duration as
        # the default settings are to only check for expiry every 2 minutes or so.
        monkeypatch.setattr(directory, 'DIRECTORY_EXPIRY_FREQUENCY', 60)
        monkeypatch.setattr(directory, 'DIRECTORY_EXPIRY_DURATION', 0.2)

        end_time: 0.0
        expiry_time: 0.0

        async def callback():
            # Validate that the item is still in the list if it has not
            # reached expiry time yet.
            if time.monotonic() < expiry_time:
                assert len(controller.lookup_all_endpoints()) == 1

            runner.cancel = time.monotonic() >= end_time

        runner = Runner()
        controller = DirectoryController()
        controller.register(runner)

        before = time.monotonic()
        controller.register_endpoint("1.2.3.4", "alpha", "role")
        assert len(controller.lookup_all_endpoints()) == 1
        assert controller._directory["alpha"].expiry_time >= before + 0.2
        expiry_time = controller._directory["alpha"].expiry_time

        # Now continue to run until expiration
        end_time = before + 1
        runner.run(callback)
        assert time.monotonic() >= end_time
        assert len(controller.lookup_all_endpoints()) == 0

    def test_heartbeat_endpoint(self) -> None:
        """
        Validates that the heartbeat_from_endpoint() function just forwards
        to register_endpoint().
        """
        controller = DirectoryController()
        assert len(controller.lookup_all_endpoints()) == 0

        controller.heartbeat_from_endpoint("a.b.C.D", "AlPhA", "ROLE")
        assert len(controller.lookup_all_endpoints()) == 1
        assert "alpha" in controller._directory
        assert controller._directory["alpha"].role == "role"
        assert controller._directory["alpha"].address == "a.b.c.d"

    def test_lookup_all_endpoints(self) -> None:
        """
        Validates that all endpoints are returned.
        """
        controller = DirectoryController()
        assert len(controller.lookup_all_endpoints()) == 0

        # Lookup an empty list
        assert controller.lookup_all_endpoints() == {}

        # Add in a single entry.
        controller.register_endpoint("1.2.3.4", "alpha", "path")
        assert controller.lookup_all_endpoints() == {"alpha": "1.2.3.4"}

        # Add in more entries.
        controller.register_endpoint("a.b.c.d", "beta", "witch")
        controller.register_endpoint("7.8.9.0", "gamma", "spiders")

        assert controller.lookup_all_endpoints() == {"alpha": "1.2.3.4", "beta": "a.b.c.d", "gamma": "7.8.9.0"}

    def test_lookup_endpoint_by_name(self) -> None:
        """
        Validates that the correct endpoint address is returned based on the provided name.
        """
        controller = DirectoryController()

        # Add in some entries
        controller.register_endpoint("1.2.3.4", "alpha", "path")
        controller.register_endpoint("a.b.c.d", "beta", "witch")
        controller.register_endpoint("7.8.9.0", "gamma", "spiders")

        # Use invalid names
        assert controller.lookup_endpoint_by_name(None) is None
        assert controller.lookup_endpoint_by_name("") is None
        assert controller.lookup_endpoint_by_name("    ") is None

        # Use unknown name
        assert controller.lookup_endpoint_by_name("delta") is None

        # Use valid names.
        assert controller.lookup_endpoint_by_name("alpha") == "1.2.3.4"
        assert controller.lookup_endpoint_by_name("ALPHA") == "1.2.3.4"
        assert controller.lookup_endpoint_by_name("BetA") == "a.b.c.d"
        assert controller.lookup_endpoint_by_name("gAmMa") == "7.8.9.0"

    def test_lookup_endpoints_by_role(self) -> None:
        """
        Validates that the correct endpoints are returned based on the
        role. Multiple items can be returned as roles do not need to be unique
        """
        controller = DirectoryController()

        # Add in some entries
        controller.register_endpoint("1.2.3.4", "alpha", "path")
        controller.register_endpoint("a.b.c.d", "beta", "witch")
        controller.register_endpoint("7.8.9.0", "gamma", "path")

        # Use invalid names
        assert controller.lookup_endpoints_by_role(None) is None
        assert controller.lookup_endpoints_by_role("") is None
        assert controller.lookup_endpoints_by_role("    ") is None

        assert controller.lookup_endpoints_by_role("spiders") == {}
        assert controller.lookup_endpoints_by_role("PATH") == {"alpha": "1.2.3.4", "gamma": "7.8.9.0"}
        assert controller.lookup_endpoints_by_role("wItCh") == {"beta": "a.b.c.d"}
