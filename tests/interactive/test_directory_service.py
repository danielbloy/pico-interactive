import json as json_module
from collections.abc import Callable, Awaitable
from types import TracebackType
from typing import Optional, Type

from adafruit_httpserver import GET, POST, OK_200, Status
from adafruit_requests import Response

from directory import DirectoryService
from interactive.network import NetworkController
from runner import Runner
from test_network import MockServer

# This is used to mock out the network.send_message function to avoid us actually sending
# network calls during the tests.
msg_url: str = ""
msg_data: str = ""
msg_json: str = ""


class MockResponse:
    def __init__(self, status: Status) -> None:
        self.encoding = "utf-8"
        self._status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type: Optional[Type[type]], exc_value: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> None:
        pass

    def close(self) -> None:
        pass


def mock_send_message(path: str, host: str = "<default>", protocol: str = "http", method="GET", data=None,
                      json=None) -> Response:
    global msg_url, msg_data, msg_json
    msg_url = f"{method} {protocol}://{host}/{path}"
    msg_data = data
    msg_json = json_module.dumps(json)

    return MockResponse(OK_200)


class TestDirectoryService:
    def test_routes(self) -> None:
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
        server = MockServer()
        controller = NetworkController(server)
        assert add_task_count == 0
        controller.register(runner)
        assert add_task_count == 2
        assert server.start_called_count == 1
        assert server.stop_called_count == 0
        assert server.poll_called_count == 0

    def test_registering_with_runner_with_coordinator(self, monkeypatch) -> None:
        """
        Validates the NetworkController registers with the Runner and with coordinator.
        This will also register its internal directory controller.
        """
        add_task_count: int = 0

        monkeypatch.setattr(network, 'NODE_COORDINATOR', "127.0.0.1")

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

        monkeypatch.setattr(network, 'register', register)

        runner = TestRunner()
        server = MockServer()
        controller = NetworkController(server)
        assert add_task_count == 0
        controller.register(runner)
        assert add_task_count == 3
        assert server.start_called_count == 1
        assert server.stop_called_count == 0
        assert server.poll_called_count == 0

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

        monkeypatch.setattr(network, 'send_heartbeat_message', heartbeat)
        monkeypatch.setattr(network, 'send_register_message', register)
        monkeypatch.setattr(network, 'send_unregister_message', unregister)

        called_count: int = 0

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= 5

        runner = Runner()
        server = MockServer()
        controller = NetworkController(server)
        controller.register(runner)
        runner.run(callback)

        assert called_count == 5
        assert server.start_called_count == 1
        assert server.stop_called_count == 1
        assert server.poll_called_count > 5

        assert heartbeat_called_count == 0
        assert register_called_count == 0
        assert unregister_called_count == 0

        # Now we setup the coordinator variables so we should get a register,
        # unregister and some heartbeat messages.
        monkeypatch.setattr(network, 'NODE_COORDINATOR', "123.45.67.89")
        monkeypatch.setattr(network, 'NETWORK_HEARTBEAT_FREQUENCY', control.RUNNER_DEFAULT_CALLBACK_FREQUENCY)

        called_count = 0

        runner = Runner()
        server = MockServer()
        controller = NetworkController(server)
        controller.register(runner)
        runner.run(callback)

        assert called_count == 5
        assert server.start_called_count == 1
        assert server.stop_called_count == 1
        assert server.poll_called_count > 5

        assert heartbeat_called_count < 5
        assert register_called_count == 1
        assert unregister_called_count == 1

# print(request)
# print(f"METHOD ... : '{request.method}'")
# print(f"PATH ..... : '{request.path}'")
# print(f"QPARAMS .. : '{request.query_params}'")
# print(f"HTTPV .... : '{request.http_version}'")
# print(f"HEADERS .. : '{request.headers}'")
# print(f"BODY ..... : '{request.body}'")
# print(f"RAW ...... : '{request.raw_request}'")
