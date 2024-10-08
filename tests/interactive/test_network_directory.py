from collections.abc import Callable

import pytest
from adafruit_httpserver import GET, POST, NOT_IMPLEMENTED_501, PUT, OK_200, Request
from adafruit_requests import Response

from directory import DirectoryController
from interactive import network
from test_network import mock_send_message, validate_methods, MockRequest


class TestRoutes:
    """
    NOTE: Even though these tests all specify (or at least try to) the correct route
          in the TestRequest(), those routes are not typically needed for the test methods
          as they expect to have been routed to correctly anyway.
    """

    @pytest.fixture(autouse=True)
    def send_message_patched(self, monkeypatch):
        monkeypatch.setattr(network, 'send_message', mock_send_message)

    @staticmethod
    def check_directory_method_conforms(
            monkeypatch, route: str, func: Callable[[Request, DirectoryController], Response]) -> None:
        """
        Simple validation checks that the register, unregister and heartbeat
        functions should follow.
        """
        # When there is a coordinator nothing should error; except when there is no directory specified.
        monkeypatch.setattr(network, 'NODE_COORDINATOR', "node")
        validate_methods({GET, POST, PUT}, route, func, DirectoryController())

        # Should always error if no directory controller is specified.
        with pytest.raises(ValueError):
            func(MockRequest(GET, route), None)

        func(MockRequest(GET, route), DirectoryController())
        func(MockRequest(PUT, route), DirectoryController())
        func(MockRequest(POST, route), DirectoryController())

        # When there is no coordinator should error but only if it is a POST or PUT
        monkeypatch.setattr(network, 'NODE_COORDINATOR', None)

        # Should always error if no directory controller is specified.
        with pytest.raises(ValueError):
            func(MockRequest(GET, route), None)

        func(MockRequest(GET, route), DirectoryController())

        with pytest.raises(ValueError):
            func(MockRequest(PUT, route), DirectoryController())

        with pytest.raises(ValueError):
            func(MockRequest(POST, route), DirectoryController())

    def test_register_errors_correctly(self, monkeypatch) -> None:
        """
        Runs the basic validation checks expected of the three main directory methods.
        """
        self.check_directory_method_conforms(monkeypatch, "/register", network.register)

    def test_register(self, monkeypatch) -> None:
        """
        TODO
        """
        monkeypatch.setattr(network, 'NODE_COORDINATOR', "node")

        controller = DirectoryController()

        validate_methods({GET, POST, PUT}, "/register", network.register, controller)

        request = MockRequest(GET, "/register")
        response = network.register(request, controller)
        assert response._body == 'registered with coordinator'
        assert response._status == OK_200

        request = MockRequest(POST, "/register")
        response = network.register(request, controller)
        assert response._body == network.OK
        assert response._status == OK_200

        request = MockRequest(PUT, "/register")
        response = network.register(request, controller)
        assert response._body == network.OK
        assert response._status == OK_200

        assert False  # Need to intercept network message and also validate directory.

    def test_unregister_errors_correctly(self, monkeypatch) -> None:
        """
        Runs the basic validation checks expected of the three main directory methods.
        """
        self.check_directory_method_conforms(monkeypatch, "/unregister", network.unregister)

    def test_unregister(self, monkeypatch) -> None:
        """
        TODO
        """
        monkeypatch.setattr(network, 'NODE_COORDINATOR', "node")

        controller = DirectoryController()

        validate_methods({GET, POST, PUT}, "/unregister", network.unregister, controller)

        request = MockRequest(GET, "/unregister")
        response = network.unregister(request, controller)
        assert response._body == 'unregistered from coordinator'
        assert response._status == OK_200

        request = MockRequest(POST, "/unregister")
        response = network.unregister(request, controller)
        assert response._body == network.OK
        assert response._status == OK_200

        request = MockRequest(PUT, "/unregister")
        response = network.unregister(request, controller)
        assert response._body == network.OK
        assert response._status == OK_200

        assert False  # Need to intercept network message and also validate directory.

    def test_heartbeat_errors_correctly(self, monkeypatch) -> None:
        """
        Runs the basic validation checks expected of the three main directory methods.
        """
        self.check_directory_method_conforms(monkeypatch, "/heartbeat", network.heartbeat)

    def test_heartbeat(self, monkeypatch) -> None:
        """
        TODO
        """
        monkeypatch.setattr(network, 'NODE_COORDINATOR', "node")

        controller = DirectoryController()

        validate_methods({GET, POST, PUT}, "/heartbeat", network.heartbeat, controller)

        request = MockRequest(GET, "/heartbeat")
        response = network.heartbeat(request, controller)
        assert response._body == 'heartbeat message sent to coordinator'
        assert response._status == OK_200

        request = MockRequest(POST, "/heartbeat")
        response = network.heartbeat(request, controller)
        assert response._body == 'TODO heartbeat message received from node'
        assert response._status == OK_200

        request = MockRequest(PUT, "/heartbeat")
        response = network.heartbeat(request, controller)
        assert response._body == 'TODO heartbeat message received from node'
        assert response._status == OK_200

        assert False  # Need to intercept network message and also validate directory.

    def test_lookup_all(self) -> None:
        """
        Validates that lookup_all() returns NOT_IMPLEMENTED_501 with no additional headers.
        """
        controller = DirectoryController()

        validate_methods({GET}, "/lookup/all", network.lookup_all, controller)

        request = MockRequest(GET, "/lookup/all")
        response = network.lookup_all(request, controller)
        assert response._body == network.NO
        assert response._status == NOT_IMPLEMENTED_501

        assert False  # Need to intercept network message and also validate directory.

    def test_lookup_name(self) -> None:
        """
        Validates that lookup_name() returns NOT_IMPLEMENTED_501 with no additional headers.
        """
        controller = DirectoryController()

        validate_methods({GET}, "/lookup/name/<name>", network.lookup_name, controller, "NAME")

        request = MockRequest(GET, "/lookup/name/<name>")
        response = network.lookup_name(request, controller, "")
        assert response._body == network.NO
        assert response._status == NOT_IMPLEMENTED_501

        assert False  # Need to intercept network message and also validate directory.

    def test_lookup_role(self) -> None:
        """
        Validates that lookup_role() returns NOT_IMPLEMENTED_501 with no additional headers.
        """
        controller = DirectoryController()

        validate_methods({GET}, "/lookup/role/<role>", network.lookup_role, controller, "ROLE")

        request = MockRequest(GET, "/lookup/role/<role>")
        response = network.lookup_role(request, controller, "")
        assert response._body == network.NO
        assert response._status == NOT_IMPLEMENTED_501

        assert False  # Need to intercept network message and also validate directory.


class TestMessages:

    @pytest.fixture(autouse=True)
    def send_message_patched(self, monkeypatch):
        monkeypatch.setattr(network, 'send_message', mock_send_message)

    def test_send_register_message(self) -> None:
        assert network.send_register_message(None) == "registered with coordinator"

    def test_receive_register_message(self) -> None:
        assert network.receive_register_message(None) == network.OK

    def test_send_unregister_message(self) -> None:
        assert network.send_unregister_message(None) == "unregistered from coordinator"

    def test_receive_unregister_message(self) -> None:
        assert network.receive_unregister_message(None) == network.OK

    def test_send_heartbeat_message(self) -> None:
        assert network.send_heartbeat_message(None) == "heartbeat message sent to coordinator"

    def test_receive_heartbeat_message(self) -> None:
        assert network.receive_heartbeat_message(None) == "TODO heartbeat message received from node"

# print(request)
# print(f"METHOD ... : '{request.method}'")
# print(f"PATH ..... : '{request.path}'")
# print(f"QPARAMS .. : '{request.query_params}'")
# print(f"HTTPV .... : '{request.http_version}'")
# print(f"HEADERS .. : '{request.headers}'")
# print(f"RAW ...... : '{request.raw_request}'")


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
