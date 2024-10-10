import asyncio
from collections.abc import Callable, Awaitable

import pytest
from adafruit_httpserver import GET, POST

import interactive.directory as directory
from interactive.control import RUNNER_DEFAULT_CALLBACK_FREQUENCY
from interactive.directory import DirectoryService
from interactive.runner import Runner
from test_directory_messages import mock_send_message
from test_network import MockRequest


class TestDirectoryService:

    @pytest.fixture(autouse=True)
    def send_message_patched(self, monkeypatch):
        monkeypatch.setattr(directory, 'send_message', mock_send_message)

    def test_routes(self) -> None:
        """
        Validates the set of routes is as expected.
        """
        service = DirectoryService()

        assert len(service.get_routes()) == 6
        assert [route for route in service.get_routes() if route.path == "/register" and route.methods == {GET, POST}]
        assert [route for route in service.get_routes() if route.path == "/unregister" and route.methods == {GET, POST}]
        assert [route for route in service.get_routes() if route.path == "/heartbeat" and route.methods == {GET, POST}]
        assert [route for route in service.get_routes() if route.path == "/lookup/all" and route.methods == {GET}]
        assert [route for route in service.get_routes() if
                route.path == "/lookup/name/<name>" and route.methods == {GET}]
        assert [route for route in service.get_routes() if
                route.path == "/lookup/role/<role>" and route.methods == {GET}]

    def test_service_routes_configured_correctly(self, monkeypatch) -> None:
        """
        Validates that the service routes are wired up correctly.
        """
        monkeypatch.setattr(directory, 'NODE_COORDINATOR', "127.0.0.1")

        service = DirectoryService()

        # Now call each of the routes. All we are doing here is validating that they
        # are wired up correctly and as expected, not that they do anything useful.
        # Later tests will perform those checks.
        #
        # NOTE: This needs to be done in an async loop.
        async def __execute():
            for route in service.get_routes():
                request = MockRequest(GET, route.path)

                # We need to handle the methods that have parameters differently
                if route.path == "/lookup/name/<name>" or route.path == "/lookup/role/<role>":
                    route.handler(request, "single parameter")
                else:
                    route.handler(request)

        asyncio.run(__execute())

    def test_registering_with_runner(self) -> None:
        """
        Validates the DirectoryService registers with the Runner, no coordinator.
        This will register itself and its internal directory controller.
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
        service = DirectoryService()
        assert add_task_count == 0
        service.register(runner)
        assert add_task_count == 2

    def test_registering_with_runner_with_coordinator(self, monkeypatch) -> None:
        """
        Validates the DirectoryService registers with the Runner and with coordinator.
        This will also register its internal directory controller.
        """
        add_task_count: int = 0

        monkeypatch.setattr(directory, 'NODE_COORDINATOR', "127.0.0.1")

        class TestRunner(Runner):
            def add_loop_task(self, task: Callable[[], Awaitable[None]]) -> None:
                nonlocal add_task_count
                add_task_count += 1

            def add_task(self, task: Callable[[], Awaitable[None]]) -> None:
                nonlocal add_task_count
                add_task_count += 1

        # Monkey patch register out as we don't actually want to perform the register.
        def register(request):
            pass

        monkeypatch.setattr(directory, 'register', register)

        runner = TestRunner()
        service = DirectoryService()
        assert add_task_count == 0
        service.register(runner)
        assert add_task_count == 3

    def test_heartbeats(self, monkeypatch) -> None:
        """
        Validates that the register, unregister and heartbeat messages are not sent
        when there is no coordinator set (the default).

        Also validates that the register, unregister and heartbeat messages are sent
        at the correct points and intervals when a coordinator is set.
        """
        heartbeat_called_count = 0
        register_called_count = 0
        unregister_called_count = 0

        def heartbeat(node):
            nonlocal heartbeat_called_count, register_called_count, unregister_called_count
            assert node == "123.45.67.89"
            assert register_called_count == 1
            assert unregister_called_count == 0
            heartbeat_called_count += 1

        def register(node):
            nonlocal heartbeat_called_count, register_called_count, unregister_called_count
            assert node == "123.45.67.89"
            assert register_called_count == 0
            assert heartbeat_called_count == 0
            assert unregister_called_count == 0
            register_called_count += 1

        def unregister(node):
            nonlocal heartbeat_called_count, register_called_count, unregister_called_count
            assert node == "123.45.67.89"
            assert register_called_count == 1
            assert unregister_called_count == 0
            assert heartbeat_called_count > 1
            unregister_called_count += 1

        monkeypatch.setattr(directory, 'send_heartbeat_message', heartbeat)
        monkeypatch.setattr(directory, 'send_register_message', register)
        monkeypatch.setattr(directory, 'send_unregister_message', unregister)

        called_count: int = 0

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= 5

        runner = Runner()
        service = DirectoryService()
        service.register(runner)
        runner.run(callback)

        assert called_count == 5
        assert heartbeat_called_count == 0
        assert register_called_count == 0
        assert unregister_called_count == 0

        # Now we setup the coordinator variables so we should get a register,
        # unregister and some heartbeat messages.
        monkeypatch.setattr(directory, 'NODE_COORDINATOR', "123.45.67.89")
        monkeypatch.setattr(directory, 'NETWORK_HEARTBEAT_FREQUENCY', RUNNER_DEFAULT_CALLBACK_FREQUENCY)

        called_count = 0

        runner = Runner()
        service = DirectoryService()
        service.register(runner)
        runner.run(callback)

        assert called_count == 5
        assert heartbeat_called_count < 5
        assert register_called_count == 1
        assert unregister_called_count == 1
