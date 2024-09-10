import asyncio
import os
import socket
from collections.abc import Callable, Awaitable

import pytest
from adafruit_httpserver import Server, GET, POST, Request, OK_200, NOT_IMPLEMENTED_501

import control
import network
from configuration import NODE_NAME, NODE_ROLE
from interactive import configuration
from network import NetworkController, HEADER_NAME, HEADER_ROLE
from polyfills import cpu
from runner import Runner


class TestServer(Server):
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

    def test_server_configured_correctly(self) -> None:
        """
        Validates that the server is setup correctly. This ignores that there
        may be a coordinator or not.
        """
        server = TestServer()
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
        assert [route for route in server._routes if route.path == "/register" and route.methods == {GET, POST}]
        assert [route for route in server._routes if route.path == "/unregister" and route.methods == {GET, POST}]
        assert [route for route in server._routes if route.path == "/heartbeat" and route.methods == {GET, POST}]
        assert [route for route in server._routes if route.path == "/restart" and route.methods == {GET}]
        assert [route for route in server._routes if route.path == "/alive" and route.methods == {GET}]
        assert [route for route in server._routes if route.path == "/name" and route.methods == {GET}]
        assert [route for route in server._routes if route.path == "/role" and route.methods == {GET}]
        assert [route for route in server._routes if route.path == "/details" and route.methods == {GET}]
        assert [route for route in server._routes if route.path == "/lookup/all" and route.methods == {GET}]
        assert [route for route in server._routes if
                route.path == "/lookup/name/<name>" and route.methods == {GET}]
        assert [route for route in server._routes if
                route.path == "/lookup/role/<role>" and route.methods == {GET}]
        assert [route for route in server._routes if route.path == "/led/blink" and route.methods == {GET}]
        assert [route for route in server._routes if route.path == "/led/<state>" and route.methods == {GET, POST}]

        # Check the server has started.
        assert not server.stopped
        assert server.start_called_count == 1
        assert server.stop_called_count == 0
        assert server.poll_called_count == 0

    def test_registering_with_runner(self) -> None:
        """
        Validates the NetworkController registers with the Runner, no coordinator.
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
        server = TestServer()
        controller = NetworkController(server)
        assert add_task_count == 0
        controller.register(runner)
        assert add_task_count == 1
        assert server.start_called_count == 1
        assert server.stop_called_count == 0
        assert server.poll_called_count == 0

    def test_registering_with_runner_with_coordinator(self, monkeypatch) -> None:
        """
        Validates the NetworkController registers with the Runner, with coordinator.
        """
        add_task_count: int = 0

        monkeypatch.setattr(configuration, 'NODE_COORDINATOR', "127.0.0.1")

        class TestRunner(Runner):
            def add_loop_task(self, task: Callable[[], Awaitable[None]]) -> None:
                nonlocal add_task_count
                add_task_count += 1

            def add_task(self, task: Callable[[], Awaitable[None]]) -> None:
                nonlocal add_task_count
                add_task_count += 1

        def register(request):
            print(request)

        network.register = register

        runner = TestRunner()
        server = TestServer()
        controller = NetworkController(server)
        assert add_task_count == 0
        controller.register(runner)
        assert add_task_count == 2
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
        server = TestServer()
        controller = NetworkController(server)
        controller.register(runner)

        runner.run(callback)
        assert called_count == 5
        assert server.start_called_count == 1
        assert server.stop_called_count == 1
        assert server.poll_called_count > 5

    def test_heartbeats(self, monkeypatch) -> None:
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

        monkeypatch.setattr(configuration, 'NODE_COORDINATOR', "123.45.67.89")
        monkeypatch.setattr(control, 'NETWORK_HEARTBEAT_FREQUENCY', control.RUNNER_DEFAULT_CALLBACK_FREQUENCY)
        monkeypatch.setattr(network, 'send_heartbeat_message', heartbeat)
        monkeypatch.setattr(network, 'send_register_message', register)
        monkeypatch.setattr(network, 'send_unregister_message', unregister)

        called_count: int = 0

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= 5

        runner = Runner()
        server = TestServer()
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


class TestRequest(Request):
    def __init__(self, method, route: str, body: str = None):
        server = TestServer()
        raw_request = bytes(
            f"{method} {route} HTTP/1.1\r\nHost: 127.0.0.1:5001\r\nUser-Agent: test-framework\r\nAccept: */*\r\n\r\n{body}",
            "utf-8")
        super().__init__(server, None, ('123.45.67.89', 12345), raw_request)


class TestHttpRoutes:
    """
    NOTE: Even though these tests all specify (or at least try to) the correct route
          in the TestRequest(), those routes are not typically needed for the test methods
          as they expect to have been routed to correctly anyway.
    """

    def test_index_returns_index_html_with_get(self) -> None:
        """
        Validates that the index.html file is returned with no additional headers.
        """
        path = os.getcwd()
        try:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            os.chdir(os.path.join(dir_path, "../.."))
            request = TestRequest("GET", "/")
            response = network.index(request)
            assert response._filename == "index.html"
            assert response._root_path == 'interactive/html'
            assert response._status == OK_200
            assert len(response._headers) == 0
        finally:
            os.chdir(path)

    def test_cpu_information(self) -> None:
        """
        Validates that the cpu information is returned with no additional headers.
        """
        request = TestRequest("GET", "/cpu-information")
        response = network.cpu_information(request)
        assert response._data == cpu.info()
        assert response._status == OK_200
        assert len(response._headers) == 0

    def test_inspect(self) -> None:
        """
        Validates that the inspect web page is returned with no additional headers.
        """
        request = TestRequest("GET", "/inspect")
        response = network.inspect(request)
        assert response._body == "TODO inspect"
        assert response._status == OK_200
        assert len(response._headers) == 0

    def test_register(self) -> None:
        assert False

    def test_unregister(self) -> None:
        assert False

    def test_heartbeat(self) -> None:
        assert False

    def test_restart(self, monkeypatch) -> None:
        """
        Validates that restart returns with no additional headers. The restart
        won't actually restart a Desktop PC as the polyfill is a noop; though
        we monkeypatch the restart() function anyway.
        """
        restart_called_count = 0

        def test_restart_fn():
            nonlocal restart_called_count
            restart_called_count += 1

        monkeypatch.setattr(network, 'cpu_restart', test_restart_fn)

        # Create an event loop which is needed for the async restart request.
        request = TestRequest("GET", "/restart")

        async def __execute():
            # Before calling the request, there should only be a single
            # async task which is this one.
            assert len(asyncio.all_tasks()) == 1
            response = network.restart(request)
            assert response._body == network.YES
            assert response._status == OK_200

            # There should now be 2 tasks, this one and the restart async task.
            assert len(asyncio.all_tasks()) == 2

            # Await for long enough for the restart to get executed.
            while len(asyncio.all_tasks()) > 1:
                await asyncio.sleep(0.1)

        asyncio.run(__execute())
        assert restart_called_count == 1

    def test_alive(self) -> None:
        """
        Validates that alive returns with no additional headers.
        """
        request = TestRequest("GET", "/alive")
        response = network.alive(request)
        assert response._body == network.YES
        assert response._status == OK_200

    def test_name(self) -> None:
        """
        Validates that name returns with no additional headers.
        """
        request = TestRequest("GET", "/name")
        response = network.name(request)
        assert response._body == configuration.NODE_NAME
        assert response._status == OK_200

    def test_role(self) -> None:
        """
        Validates that role returns with no additional headers.
        """
        request = TestRequest("GET", "/role")
        response = network.role(request)
        assert response._body == configuration.NODE_ROLE
        assert response._status == OK_200

    def test_details(self) -> None:
        """
        Validates that the details information is returned with no additional headers.
        """
        request = TestRequest("GET", "/details")
        response = network.details(request)
        assert response._data == configuration.details()
        assert response._status == OK_200
        assert len(response._headers) == 0

    def test_led_blink(self, monkeypatch) -> None:
        """
        Validates the led_blink route calls the appropriate receive function.
        """
        message_called_count = 0

        def test_message_fn(r: Request) -> str:
            nonlocal message_called_count
            message_called_count += 1
            return 'LED has blinked'

        monkeypatch.setattr(network, 'receive_blink_message', test_message_fn)

        request = TestRequest("GET", "/led/blink")
        response = network.led_blink(request)
        assert response._body == 'LED has blinked'
        assert response._status == OK_200
        assert len(response._headers) == 0

        assert message_called_count == 1

    def test_led_state(self, monkeypatch) -> None:
        """
        Validates the led_state() returns the desired state..
        """
        message_called_count = 0

        def test_message_fn(request: Request, state: str) -> str:
            nonlocal message_called_count
            message_called_count += 1
            return f'LED is {state}'

        monkeypatch.setattr(network, 'receive_led_message', test_message_fn)

        request = TestRequest("GET", "/led/<state>")
        response = network.led_state(request, "ON")
        assert response._body == 'LED is ON'
        assert response._status == OK_200
        assert len(response._headers) == 0

        assert message_called_count == 1

        response = network.led_state(request, "OFF")
        assert response._body == 'LED is OFF'
        assert response._status == OK_200
        assert len(response._headers) == 0

        assert message_called_count == 2

    def test_lookup_all(self) -> None:
        """
        Validates that lookup_all() returns NOT_IMPLEMENTED_501 with no additional headers.
        """
        request = TestRequest("GET", "/lookup/all")
        response = network.lookup_all(request)
        assert response._body == network.NO
        assert response._status == NOT_IMPLEMENTED_501

    def test_lookup_name(self) -> None:
        """
        Validates that lookup_name() returns NOT_IMPLEMENTED_501 with no additional headers.
        """
        request = TestRequest("GET", "/lookup/name/<name>")
        response = network.lookup_name(request, "")
        assert response._body == network.NO
        assert response._status == NOT_IMPLEMENTED_501

    def test_lookup_role(self) -> None:
        """
        Validates that lookup_role() returns NOT_IMPLEMENTED_501 with no additional headers.
        """
        request = TestRequest("GET", "/lookup/role/<role>")
        response = network.lookup_role(request, "")
        assert response._body == network.NO
        assert response._status == NOT_IMPLEMENTED_501


def mock_send_message(path: str, host: str = configuration.NODE_COORDINATOR,
                      protocol: str = "http", method="GET",
                      data=None, json=None):
    print("mock_send_message")
    pass


class TestMessages:

    @pytest.fixture(autouse=True)
    def send_message_patched(self, monkeypatch):
        monkeypatch.setattr(network, 'send_message', mock_send_message)

    def test_send_message(self) -> None:
        network.send_message("hi")
        assert False

    def test_send_register_message(self) -> None:
        assert False

    def test_receive_register_message(self) -> None:
        assert False

    def test_send_unregister_message(self) -> None:
        assert False

    def test_receive_unregister_message(self) -> None:
        assert False

    def test_send_heartbeat_message(self) -> None:
        assert False

    def test_receive_heartbeat_message(self) -> None:
        assert False

    def test_receive_blink_message(self) -> None:
        assert False

    def test_receive_led_message(self) -> None:
        assert False

# C:\Users\danie>curl --verbose http://127.0.0.1:5001/index.html
# *   Trying 127.0.0.1:5001...
# * Connected to 127.0.0.1 (127.0.0.1) port 5001
# > GET /index.html HTTP/1.1
# > Host: 127.0.0.1:5001
# > User-Agent: curl/8.8.0
# > Accept: */*
# >
# * Request completely sent off
# < HTTP/1.1 200 OK
# < name: <hostname>
# < role: <host role>
# < content-type: text/html
# < content-length: 345
# < connection: close
# <
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta http-equiv="X-UA-Compatible" content="IE=edge">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Pico Interactive</title>
# </head>
# <body>
# <p>Hello from the <strong>CircuitPython HTTP Server!</strong></p>
# </body>
# </html>
# * Closing connection

# Server
# <Request "GET /index.html">
# METHOD ... : 'GET'
# PATH ..... : '/index.html'
# QPARAMS .. : ''
# HTTPV .... : 'HTTP/1.1'
# HEADERS .. : '<Headers {'host': ['127.0.0.1:5001'], 'user-agent': ['curl/8.8.0'], 'accept': ['*/*']}>'
# RAW ...... : 'b'GET /index.html HTTP/1.1\r\nHost: 127.0.0.1:5001\r\nUser-Agent: curl/8.8.0\r\nAccept: */*\r\n\r\n''


# C:\Users\danie>  curl --verbose http://127.0.0.1:5001/register -X POST -H "Content-Type: application/json" -d "{\"key1\":\"value1\", \"key2\":\"value2\"}"
# Note: Unnecessary use of -X or --request, POST is already inferred.
# *   Trying 127.0.0.1:5001...
# * Connected to 127.0.0.1 (127.0.0.1) port 5001
# > POST /register HTTP/1.1
# > Host: 127.0.0.1:5001
# > User-Agent: curl/8.8.0
# > Accept: */*
# > Content-Type: application/json
# > Content-Length: 34
# >
# * upload completely sent off: 34 bytes
# < HTTP/1.1 200 OK
# < name: <hostname>
# < role: <host role>
# < content-type: text/plain
# < content-length: 2
# < connection: close
# <
# OK* Closing connection

# Server
# <Request "POST /register">
# METHOD ... : 'POST'
# PATH ..... : '/register'
# QPARAMS .. : ''
# HTTPV .... : 'HTTP/1.1'
# HEADERS .. : '<Headers {'host': ['127.0.0.1:5001'], 'user-agent': ['curl/8.8.0'], 'accept': ['*/*'], 'content-type': ['application/json'], 'content-length': ['34']}>'
# RAW ...... : 'b'POST /register HTTP/1.1\r\nHost: 127.0.0.1:5001\r\nUser-Agent: curl/8.8.0\r\nAccept: */*\r\nContent-Type: application/json\r\nContent-Length: 34\r\n\r\n{"key1":"value1", "key2":"value2"}''


# C:\Users\danie>curl --verbose http://127.0.0.1:5001/register
# *   Trying 127.0.0.1:5001...
# * Connected to 127.0.0.1 (127.0.0.1) port 5001
# > GET /register HTTP/1.1
# > Host: 127.0.0.1:5001
# > User-Agent: curl/8.8.0
# > Accept: */*
# >
# < HTTP/1.1 200 OK
# < name: <hostname>
# < role: <host role>
# < content-type: text/plain
# < content-length: 27
# < connection: close
# <
# registered with coordinator* we are done reading and this is set to close, stop send
# * Closing connection

# Server
# <Request "GET /register">
# METHOD ... : 'GET'
# PATH ..... : '/register'
# QPARAMS .. : ''
# HTTPV .... : 'HTTP/1.1'
# HEADERS .. : '<Headers {'host': ['127.0.0.1:5001'], 'user-agent': ['curl/8.8.0'], 'accept': ['*/*']}>'
# RAW ...... : 'b'GET /register HTTP/1.1\r\nHost: 127.0.0.1:5001\r\nUser-Agent: curl/8.8.0\r\nAccept: */*\r\n\r\n''
