import asyncio
import socket
from collections.abc import Callable, Awaitable

import pytest
from adafruit_httpserver import Server, GET, POST, Request, OK_200, NOT_IMPLEMENTED_501, NOT_FOUND_404, PUT, DELETE, \
    PATCH, HEAD, OPTIONS, TRACE, CONNECT, BAD_REQUEST_400

import interactive.control as control
import interactive.network as network
from interactive.configuration import NODE_NAME, NODE_ROLE
from interactive.network import NetworkController, HEADER_NAME, HEADER_ROLE
from interactive.runner import Runner


class MockServer(Server):
    def __init__(self) -> None:
        # noinspection PyTypeChecker
        super().__init__(socket)
        self.start_called_count = 0
        self.stop_called_count = 0
        self.poll_called_count = 0

    def start(self, host: str = "0.0.0.0", port: int = 5000) -> None:
        self.start_called_count += 1
        super().start(host, port)

    def stop(self):
        self.stop_called_count += 1
        super().stop()

    def poll(self):
        self.poll_called_count += 1
        return super().poll()


class MockRequest(Request):
    def __init__(self, method, route: str, body: str = ""):
        server = MockServer()
        raw_request = bytes(
            f"{method} {route} HTTP/1.1\r\nHost: 127.0.0.1:5001\r\nUser-Agent: test-framework\r\nAccept: */*\r\n\r\n{body}",
            "utf-8")
        super().__init__(server, None, ('123.45.67.89', 12345), raw_request)


def validate_methods(valid_methods, route, fn, *args) -> None:
    """
    Validates that only the methods for the specified route are valid, all others
    should return a 404. All valid routes should return a 200 or 501.
    """
    for method in {GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS, TRACE, CONNECT}:
        request = MockRequest(method, route)
        response = fn(request, *args)

        if method in valid_methods:
            # Bad request is allowed here as it generally means the body data is not formatted correctly
            # and as we don't pass in a body we expect it to fail.
            assert response._status == OK_200 or response._status == NOT_IMPLEMENTED_501 or response._status == BAD_REQUEST_400
        else:
            assert response._body == network.NO
            assert response._status == NOT_FOUND_404


class TestNetwork:

    def test_creating_with_none_network_errors(self) -> None:
        """
        Validates that a NetworkController cannot be constructed with
        a None value.
        """
        with pytest.raises(ValueError):
            # noinspection PyTypeChecker
            NetworkController(None)

    def test_creating_with_string_errors(self) -> None:
        """
        Validates that a NetworkController cannot be constructed with
        a value that is not a Server.
        """
        with pytest.raises(ValueError):
            # noinspection PyTypeChecker
            NetworkController("")

    def test_creating_with_invalid_callback_errors(self) -> None:
        """
        Validates that a NetworkController cannot be constructed with
        a trigger_callback value that is not a Callable.
        """
        server = MockServer()
        with pytest.raises(ValueError):
            # noinspection PyTypeChecker
            NetworkController(server, "")

    def test_creating_with_valid_callback_is_fine(self) -> None:
        """
        Validates that a NetworkController can be constructed with
        a trigger_callback value that is a Callable.
        """
        server = MockServer()

        def trigger():
            pass

        # noinspection PyTypeChecker
        NetworkController(server, trigger_callback=trigger)

    def test_server_configured_correctly(self) -> None:
        """
        Validates that the server is setup correctly. This ignores that there
        may be a coordinator or not.
        """
        server = MockServer()
        controller = NetworkController(server)

        # Check there are two headers
        assert len(server.headers.items()) == 2
        assert set([item[0] for item in server.headers.items()]) == {HEADER_NAME, HEADER_ROLE}
        assert set([item[1] for item in server.headers.items()]) == {NODE_NAME, NODE_ROLE}
        assert set(server.headers.items()) == {(HEADER_NAME, NODE_NAME), (HEADER_ROLE, NODE_ROLE)}

        # Check there are some routes. We check for the presence of some of the well
        # known standard ones.
        assert len(server._routes) >= 17
        assert [route for route in server._routes if route.path == "/" and route.methods == {GET}]
        assert [route for route in server._routes if route.path == "/index.html" and route.methods == {GET}]
        assert [route for route in server._routes if route.path == "/inspect" and route.methods == {GET}]
        assert [route for route in server._routes if route.path == "/restart" and route.methods == {GET}]
        assert [route for route in server._routes if route.path == "/alive" and route.methods == {GET}]
        assert [route for route in server._routes if route.path == "/name" and route.methods == {GET}]
        assert [route for route in server._routes if route.path == "/role" and route.methods == {GET}]
        assert [route for route in server._routes if route.path == "/details" and route.methods == {GET}]
        assert [route for route in server._routes if route.path == "/blink" and route.methods == {GET}]
        assert [route for route in server._routes if route.path == "/led/blink" and route.methods == {GET}]
        assert [route for route in server._routes if route.path == "/led/<state>" and route.methods == {GET, POST}]
        assert [route for route in server._routes if route.path == "/register" and route.methods == {GET, POST}]
        assert [route for route in server._routes if route.path == "/unregister" and route.methods == {GET, POST}]
        assert [route for route in server._routes if route.path == "/heartbeat" and route.methods == {GET, POST}]
        assert [route for route in server._routes if route.path == "/lookup/all" and route.methods == {GET}]
        assert [route for route in server._routes if
                route.path == "/lookup/name/<name>" and route.methods == {GET}]
        assert [route for route in server._routes if
                route.path == "/lookup/role/<role>" and route.methods == {GET}]
        assert [route for route in server._routes if route.path == "/trigger" and route.methods == {GET}]

        # Check the server has started.
        assert not server.stopped
        assert server.start_called_count == 1
        assert server.stop_called_count == 0
        assert server.poll_called_count == 0

    def test_server_routes_configured_correctly(self, monkeypatch) -> None:
        """
        Validates that the server routes are wired up correctly.
        """
        monkeypatch.setattr(network, 'NODE_COORDINATOR', "127.0.0.1")

        server = MockServer()
        controller = NetworkController(server)

        # Now call each of the routes. All we are doing here is validating that they
        # are wired up correctly and as expected, not that they do anything useful.
        # Later tests will perform those checks.
        #
        # NOTE: This needs to be done in an async loop.
        async def __execute():
            for route in server._routes:
                request = MockRequest(GET, route.path)

                # We need to handle the methods that have parameters differently
                if (route.path == "/led/<state>"
                        or route.path == "/lookup/name/<name>"
                        or route.path == "/lookup/role/<role>"):
                    route.handler(request, "single parameter")
                else:
                    route.handler(request)

        asyncio.run(__execute())

    def test_registering_with_runner(self) -> None:
        """
        Validates the NetworkController registers with the Runner, no coordinator.
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

    def test_serve_requests(self) -> None:
        """
        Tests that serve requests gets executed and calls server.poll() as well
        as server.cancel().
        """
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
