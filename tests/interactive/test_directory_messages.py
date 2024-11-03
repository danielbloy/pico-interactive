import json as json_module
import time
from collections.abc import Callable
from types import TracebackType
from typing import Optional, Type

import pytest
from adafruit_httpserver import GET, POST, PUT, OK_200, Request, BAD_REQUEST_400, Status
from adafruit_requests import Response

from interactive import directory
from interactive.directory import DirectoryController, lookup_all, lookup_name
from interactive.directory import receive_register_message, receive_unregister_message, receive_heartbeat_message
from interactive.directory import register, unregister, heartbeat, lookup_role
from interactive.directory import send_register_message, send_unregister_message, send_heartbeat_message
from interactive.network import YES, OK
from test_network import validate_methods, MockRequest

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


class TestRoutes:
    """
    NOTE: Even though these tests all specify (or at least try to) the correct route
          in the TestRequest(), those routes are not typically needed for the test methods
          as they expect to have been routed to correctly anyway.
    """

    @pytest.fixture(autouse=True)
    def send_message_patched(self, monkeypatch):
        monkeypatch.setattr(directory, 'send_message', mock_send_message)

    @pytest.fixture(autouse=True)
    def fix_ip_address(self, monkeypatch):
        monkeypatch.setattr(directory, 'get_address', lambda: "w.x.y.z")

    @staticmethod
    def check_directory_method_conforms(
            monkeypatch, route: str, func: Callable[[Request, DirectoryController], Response]) -> None:
        """
        Simple validation checks that the register, unregister and heartbeat
        functions should follow.
        """
        json_body = '{"name":"daniel", "role":"programmer", "address":"a.b.c.d"}'
        # When there is a coordinator nothing should error; except when there is no directory specified.
        monkeypatch.setattr(directory, 'NODE_COORDINATOR', "node")
        validate_methods({GET, POST, PUT}, route, func, DirectoryController())

        # Should always error if no directory controller is specified.
        with pytest.raises(ValueError):
            func(MockRequest(GET, route, body=json_body), None)

        func(MockRequest(GET, route, body=json_body), DirectoryController())
        func(MockRequest(PUT, route, body=json_body), DirectoryController())
        func(MockRequest(POST, route, body=json_body), DirectoryController())

        # When there is no coordinator should error but only if it is a POST or PUT
        monkeypatch.setattr(directory, 'NODE_COORDINATOR', None)

        # Should always error if no directory controller is specified.
        with pytest.raises(ValueError):
            func(MockRequest(GET, route, body=json_body), None)

        with pytest.raises(ValueError):
            func(MockRequest(GET, route, body=json_body), DirectoryController())

        func(MockRequest(PUT, route, body=json_body), DirectoryController())
        func(MockRequest(POST, route, body=json_body), DirectoryController())

    def test_register_errors_correctly(self, monkeypatch) -> None:
        """
        Runs the basic validation checks expected of the three main directory methods.
        """
        self.check_directory_method_conforms(monkeypatch, "/register", register)

    def test_register(self, monkeypatch) -> None:
        """
        Validates that the register message responds to GET, PUT and POST requests
        along with the required validation and that the correct message handling functions
        are called; this assumes success each time.
        """
        global msg_url, msg_data, msg_json
        monkeypatch.setattr(directory, 'NODE_COORDINATOR', "node")

        controller = DirectoryController()

        validate_methods({GET, POST, PUT}, "/register", register, controller)

        # This registers the node with the coordinator; we validate the message is sent.
        request = MockRequest(GET, "/register")
        response = register(request, controller)
        assert response._body == YES
        assert response._status == OK_200
        assert msg_url == "GET http://node//register"
        assert msg_data == None
        assert msg_json == '{"name": "<hostname>", "role": "<host role>", "coordinator": null, "address": "w.x.y.z"}'
        assert len(controller._directory) == 0

        # Validate that a new item was registered
        request = MockRequest(POST, "/register", body='{"name":"node_1", "role":"role_1", "address":"1.2.3.4"}')
        response = register(request, controller)
        assert response._body == OK
        assert response._status == OK_200
        assert len(controller._directory) == 1
        assert "node_1" in controller._directory
        assert controller._directory["node_1"].name == "node_1"
        assert controller._directory["node_1"].role == "role_1"
        assert controller._directory["node_1"].address == "1.2.3.4"
        expiry_time = controller._directory["node_1"].expiry_time

        # Validate that a second item was registered
        request = MockRequest(POST, "/register", body='{"name":"NODE_2", "role":"role_2", "address":"6.7.8.9"}')
        response = register(request, controller)
        assert response._body == OK
        assert response._status == OK_200
        assert len(controller._directory) == 2
        assert "node_1" in controller._directory
        assert controller._directory["node_1"].name == "node_1"
        assert controller._directory["node_1"].role == "role_1"
        assert controller._directory["node_1"].address == "1.2.3.4"
        assert "node_2" in controller._directory
        assert controller._directory["node_2"].name == "node_2"
        assert controller._directory["node_2"].role == "role_2"
        assert controller._directory["node_2"].address == "6.7.8.9"

        # Validate that the first item was registered, but this time updated.
        time.sleep(0.05)
        request = MockRequest(PUT, "/register", body='{"name":"node_1", "role":"role_1", "address":"1.2.3.4"}')
        response = register(request, controller)
        assert response._body == OK
        assert response._status == OK_200
        assert len(controller._directory) == 2
        assert "node_1" in controller._directory
        assert controller._directory["node_1"].name == "node_1"
        assert controller._directory["node_1"].role == "role_1"
        assert controller._directory["node_1"].address == "1.2.3.4"
        assert controller._directory["node_1"].expiry_time > expiry_time
        assert "node_2" in controller._directory
        assert controller._directory["node_2"].name == "node_2"
        assert controller._directory["node_2"].role == "role_2"
        assert controller._directory["node_2"].address == "6.7.8.9"

    def test_unregister_errors_correctly(self, monkeypatch) -> None:
        """
        Runs the basic validation checks expected of the three main directory methods.
        """
        self.check_directory_method_conforms(monkeypatch, "/unregister", unregister)

    def test_unregister(self, monkeypatch) -> None:
        """
        Validates that the unregister message responds to GET, PUT and POST requests
        along with the required validation and that the correct message handling functions
        are called; this assumes success each time.
        """
        global msg_url, msg_data, msg_json
        monkeypatch.setattr(directory, 'NODE_COORDINATOR', "node")

        controller = DirectoryController()

        validate_methods({GET, POST, PUT}, "/unregister", unregister, controller)

        request = MockRequest(GET, "/unregister")
        response = unregister(request, controller)
        assert response._body == YES
        assert response._status == OK_200
        assert msg_url == "GET http://node//unregister"
        assert msg_data == None
        assert msg_json == '{"name": "<hostname>", "role": "<host role>", "coordinator": null, "address": "w.x.y.z"}'
        assert len(controller._directory) == 0

        # Validate unregister from an empty directory
        request = MockRequest(POST, "/unregister", body='{"name":"node_1"}')
        response = unregister(request, controller)
        assert response._body == OK
        assert response._status == OK_200
        assert len(controller._directory) == 0

        # Add some entries
        controller.register_endpoint("1.2.3.4", "node_1", "role_1")
        controller.register_endpoint("6.7.8.9", "node_2", "role_2")
        assert len(controller._directory) == 2

        # Unregister an unknown endpoint
        request = MockRequest(PUT, "/unregister", body='{"name":"node_3"}')
        response = unregister(request, controller)
        assert response._body == OK
        assert response._status == OK_200
        assert len(controller._directory) == 2

        # Unregister a known endpoint
        request = MockRequest(PUT, "/unregister", body='{"name":"node_2"}')
        response = unregister(request, controller)
        assert response._body == OK
        assert response._status == OK_200
        assert len(controller._directory) == 1
        assert "node_1" in controller._directory
        assert controller._directory["node_1"].name == "node_1"
        assert controller._directory["node_1"].role == "role_1"
        assert controller._directory["node_1"].address == "1.2.3.4"

        # Unregister the same endpoint
        request = MockRequest(PUT, "/unregister", body='{"name":"node_2"}')
        response = unregister(request, controller)
        assert response._body == OK
        assert response._status == OK_200
        assert len(controller._directory) == 1
        assert "node_1" in controller._directory
        assert controller._directory["node_1"].name == "node_1"
        assert controller._directory["node_1"].role == "role_1"
        assert controller._directory["node_1"].address == "1.2.3.4"

    def test_heartbeat_errors_correctly(self, monkeypatch) -> None:
        """
        Runs the basic validation checks expected of the three main directory methods.
        """
        self.check_directory_method_conforms(monkeypatch, "/heartbeat", heartbeat)

    def test_heartbeat(self, monkeypatch) -> None:
        """
        Validates that the heartbeat message responds to GET, PUT and POST requests
        along with the required validation and that the correct message handling functions
        are called; this assumes success each time.
        """
        global msg_url, msg_data, msg_json
        monkeypatch.setattr(directory, 'NODE_COORDINATOR', "node")

        controller = DirectoryController()

        validate_methods({GET, POST, PUT}, "/heartbeat", heartbeat, controller)

        request = MockRequest(GET, "/heartbeat")
        response = heartbeat(request, controller)
        assert response._body == YES
        assert response._status == OK_200
        assert msg_url == "GET http://node//heartbeat"
        assert msg_data == None
        assert msg_json == '{"name": "<hostname>", "role": "<host role>", "coordinator": null, "address": "w.x.y.z"}'
        assert len(controller._directory) == 0

        # Validate that a new item was registered after a heartbeat
        request = MockRequest(POST, "/heartbeat", body='{"name":"node_1", "role":"role_1", "address":"1.2.3.4"}')
        response = register(request, controller)
        assert response._body == OK
        assert response._status == OK_200
        assert len(controller._directory) == 1
        assert "node_1" in controller._directory
        assert controller._directory["node_1"].name == "node_1"
        assert controller._directory["node_1"].role == "role_1"
        assert controller._directory["node_1"].address == "1.2.3.4"
        expiry_time = controller._directory["node_1"].expiry_time

        # Validate that a second item was registered after a heartbeat
        request = MockRequest(POST, "/heartbeat", body='{"name":"NODE_2", "role":"role_2", "address":"6.7.8.9"}')
        response = register(request, controller)
        assert response._body == OK
        assert response._status == OK_200
        assert len(controller._directory) == 2
        assert "node_1" in controller._directory
        assert controller._directory["node_1"].name == "node_1"
        assert controller._directory["node_1"].role == "role_1"
        assert controller._directory["node_1"].address == "1.2.3.4"
        assert "node_2" in controller._directory
        assert controller._directory["node_2"].name == "node_2"
        assert controller._directory["node_2"].role == "role_2"
        assert controller._directory["node_2"].address == "6.7.8.9"

        # Validate that the first item has its time updated.
        time.sleep(0.05)
        request = MockRequest(PUT, "/heartbeat", body='{"name":"node_1", "role":"role_1", "address":"1.2.3.4"}')
        response = register(request, controller)
        assert response._body == OK
        assert response._status == OK_200
        assert len(controller._directory) == 2
        assert "node_1" in controller._directory
        assert controller._directory["node_1"].name == "node_1"
        assert controller._directory["node_1"].role == "role_1"
        assert controller._directory["node_1"].address == "1.2.3.4"
        assert controller._directory["node_1"].expiry_time > expiry_time
        assert "node_2" in controller._directory
        assert controller._directory["node_2"].name == "node_2"
        assert controller._directory["node_2"].role == "role_2"
        assert controller._directory["node_2"].address == "6.7.8.9"

    def test_lookup_all(self) -> None:
        """
        Validates that lookup_all() returns NOT_IMPLEMENTED_501 with no additional headers.
        """
        controller = DirectoryController()

        validate_methods({GET}, "/lookup/all", lookup_all, controller)

        # Lookup when no nodes are registered.
        request = MockRequest(GET, "/lookup/all")
        response = lookup_all(request, controller)
        assert response._data == {}
        assert response._status == OK_200

        # Register a single name and look it up.
        controller.register_endpoint("a.b.c.d", "my_node", "my_role")
        request = MockRequest(GET, "/lookup/all")
        response = lookup_all(request, controller)
        assert response._data == {'my_node': 'a.b.c.d'}
        assert response._status == OK_200

        # Register a couple more names and look them up.
        controller.register_endpoint("1.2.3.4", "node_1", "role_1")
        controller.register_endpoint("6.7.8.9", "node_2", "role_2")

        request = MockRequest(GET, "/lookup/all")
        response = lookup_all(request, controller)
        assert response._data == {'my_node': 'a.b.c.d', 'node_1': '1.2.3.4', 'node_2': '6.7.8.9'}
        assert response._status == OK_200

    def test_lookup_name(self) -> None:
        """
        Validates that lookup_name() returns NOT_IMPLEMENTED_501 with no additional headers.
        """
        controller = DirectoryController()

        validate_methods({GET}, "/lookup/name/<name>", lookup_name, controller, "NAME")

        # Lookup when no nodes are registered.
        request = MockRequest(GET, "/lookup/name/<name>")
        response = lookup_name(request, controller, "my_name")
        assert response._body == ''
        assert response._data == {"name": "my_name", "address": None}
        assert response._status == OK_200

        # Register a couple of names and look them up.
        controller.register_endpoint("1.2.3.4", "node_1", "role_1")
        controller.register_endpoint("6.7.8.9", "node_2", "role_2")

        response = lookup_name(request, controller, "NODE_1")
        assert response._body == ''
        assert response._data == {"name": "NODE_1", "address": "1.2.3.4"}
        assert response._status == OK_200

        response = lookup_name(request, controller, "NoDe_2")
        assert response._body == ''
        assert response._data == {"name": "NoDe_2", "address": "6.7.8.9"}
        assert response._status == OK_200

    def test_lookup_role(self) -> None:
        """
        Validates that lookup_role() returns NOT_IMPLEMENTED_501 with no additional headers.
        """
        controller = DirectoryController()

        validate_methods({GET}, "/lookup/role/<role>", lookup_role, controller, "ROLE")

        # Lookup when no nodes are registered.
        request = MockRequest(GET, "/lookup/<role>")
        response = lookup_role(request, controller, "role")
        assert response._data == {}
        assert response._status == OK_200

        # Register a single name and look it up.
        controller.register_endpoint("a.b.c.d", "my_node", "my_role")
        request = MockRequest(GET, "/lookup/<role>")
        response = lookup_role(request, controller, "my_role")
        assert response._data == {'my_node': 'a.b.c.d'}
        assert response._status == OK_200

        # Register a couple more names and look them up.
        controller.register_endpoint("1.2.3.4", "node_1", "role_1")
        controller.register_endpoint("w.x.y.z", "node_a", "role_1")
        controller.register_endpoint("6.7.8.9", "node_2", "role_2")

        request = MockRequest(GET, "/lookup/<role>")
        response = lookup_role(request, controller, "role_1")
        assert response._data == {'node_1': '1.2.3.4', 'node_a': 'w.x.y.z'}
        assert response._status == OK_200


class TestMessages:

    @pytest.fixture(autouse=True)
    def send_message_patched(self, monkeypatch):
        monkeypatch.setattr(directory, 'send_message', mock_send_message)

    @pytest.fixture(autouse=True)
    def fix_ip_address(self, monkeypatch):
        monkeypatch.setattr(directory, 'get_address', lambda: "w.x.y.z")

    @staticmethod
    def check_receive_method_conforms(
            route: str, func: Callable[[Request, DirectoryController], Response],
            requires_address: bool = True, requires_role: bool = True) -> None:
        """
        Simple validation checks that the register, unregister and heartbeat
        receive functions should follow.
        """
        # Should always error if no request  is specified.
        with pytest.raises(ValueError):
            func(None, DirectoryController())

        # Should always error if no directory controller is specified.
        with pytest.raises(ValueError):
            func(MockRequest(GET, route), None)

        # Should always error if no body is specified or body is invalid json
        response = func(MockRequest(GET, route, body="invalid json"), DirectoryController())
        assert response._body == "FAILED_TO_PARSE_BODY"
        assert response._status == BAD_REQUEST_400

        # Should always error if no name is provided in the body
        response = func(MockRequest(POST, route, body='{"address":"i", "role":"r"}'), DirectoryController())
        assert response._body == "NO_NAME_SPECIFIED"
        assert response._status == BAD_REQUEST_400

        # Might error if no address is provided in the body
        response = func(MockRequest(POST, route, body='{"name":"n", "role":"r"}'), DirectoryController())
        if requires_address:
            assert response._body == "NO_ADDRESS_SPECIFIED"
            assert response._status == BAD_REQUEST_400
        else:
            assert response._body == OK
            assert response._status == OK_200

        print("a")
        # Might error if no role is provided in the body
        response = func(MockRequest(POST, route, body='{"name":"n", "address":"i"}'), DirectoryController())
        if requires_role:
            assert response._body == "NO_ROLE_SPECIFIED"
            assert response._status == BAD_REQUEST_400
        else:
            assert response._body == OK
            assert response._status == OK_200

    def test_send_register_message(self) -> None:
        """
        Very simple test to check the correct format is being sent.
        """
        assert send_register_message("coordinator") == YES
        assert msg_url == "GET http://coordinator//register"
        assert msg_data == None
        assert msg_json == '{"name": "<hostname>", "role": "<host role>", "coordinator": null, "address": "w.x.y.z"}'

    def test_receive_register_errors_correctly(self) -> None:
        """
        Validates the register method correctly errors when the network request
        is incorrectly formed or missing data.
        """
        self.check_receive_method_conforms("/register", receive_register_message)

    def test_receive_register_message(self) -> None:
        """
        Validates the register method correctly extracts the JSON data and
        registers the node with the directory.
        """
        node_1 = MockRequest(POST, "/register", body='{"name":"node_1", "role":"role_1", "address":"1.2.3.4"}')
        node_2 = MockRequest(POST, "/register", body='{"name":"NODE_2", "role":"role_2", "address":"6.7.8.9"}')

        controller = DirectoryController()

        # Receive a registration with an empty directory.
        response = receive_register_message(node_1, controller)
        assert response._body == OK
        assert response._status == OK_200
        assert len(controller._directory) == 1
        assert "node_1" in controller._directory
        assert controller._directory["node_1"].name == "node_1"
        assert controller._directory["node_1"].role == "role_1"
        assert controller._directory["node_1"].address == "1.2.3.4"
        expiry_time = controller._directory["node_1"].expiry_time

        # Receive the same registration again; no change in state except time.
        time.sleep(0.05)
        response = receive_register_message(node_1, controller)
        assert response._body == OK
        assert response._status == OK_200
        assert len(controller._directory) == 1
        assert "node_1" in controller._directory
        assert controller._directory["node_1"].name == "node_1"
        assert controller._directory["node_1"].role == "role_1"
        assert controller._directory["node_1"].address == "1.2.3.4"
        assert controller._directory["node_1"].expiry_time > expiry_time

        # Receive a new registration.
        response = receive_register_message(node_2, controller)
        assert response._body == OK
        assert response._status == OK_200
        assert len(controller._directory) == 2
        assert "node_1" in controller._directory
        assert controller._directory["node_1"].name == "node_1"
        assert controller._directory["node_1"].role == "role_1"
        assert controller._directory["node_1"].address == "1.2.3.4"
        assert "node_2" in controller._directory
        assert controller._directory["node_2"].name == "node_2"
        assert controller._directory["node_2"].role == "role_2"
        assert controller._directory["node_2"].address == "6.7.8.9"

    def test_send_unregister_message(self) -> None:
        """
        Very simple test to check the correct format is being sent.
        """
        assert send_unregister_message("coordinator") == YES
        assert msg_url == "GET http://coordinator//unregister"
        assert msg_data == None
        assert msg_json == '{"name": "<hostname>", "role": "<host role>", "coordinator": null, "address": "w.x.y.z"}'

    def test_receive_unregister_errors_correctly(self) -> None:
        """
        Validates the unregister method correctly errors when the network request
        is incorrectly formed or missing data.
        """
        self.check_receive_method_conforms("/unregister", receive_unregister_message, requires_address=False,
                                           requires_role=False)

    def test_receive_unregister_message(self) -> None:
        """
        Validates the unregister method correctly extracts the JSON data and
        unregisters the node with the directory.
        """
        unknown = MockRequest(POST, "/unregister",
                              body='{"name":"unknown", "role":"role_unknown", "address":"a.b.c.d"}')
        node_1 = MockRequest(POST, "/unregister", body='{"name":"node_1", "role":"role_1", "address":"1.2.3.4"}')
        node_2 = MockRequest(POST, "/unregister", body='{"name":"NODE_2", "role":"role_2", "address":"6.7.8.9"}')

        controller = DirectoryController()

        # Receive an unregister with an empty directory
        response = receive_unregister_message(node_1, controller)
        assert response._body == OK
        assert response._status == OK_200
        assert len(controller._directory) == 0

        # Add some entries
        response = receive_register_message(node_1, controller)
        assert response._body == OK
        assert response._status == OK_200
        response = receive_register_message(node_2, controller)
        assert response._body == OK
        assert response._status == OK_200
        assert len(controller._directory) == 2

        # Receive an unregister for an unknown node
        response = receive_unregister_message(unknown, controller)
        assert response._body == OK
        assert response._status == OK_200
        assert len(controller._directory) == 2

        # Receive an unregister for a known node
        response = receive_unregister_message(node_1, controller)
        assert response._body == OK
        assert response._status == OK_200
        assert len(controller._directory) == 1
        assert "node_2" in controller._directory
        assert controller._directory["node_2"].name == "node_2"
        assert controller._directory["node_2"].role == "role_2"
        assert controller._directory["node_2"].address == "6.7.8.9"

        # Receive another unregister for the same node just unregistered
        response = receive_unregister_message(node_1, controller)
        assert response._body == OK
        assert response._status == OK_200
        assert len(controller._directory) == 1
        assert "node_2" in controller._directory
        assert controller._directory["node_2"].name == "node_2"
        assert controller._directory["node_2"].role == "role_2"
        assert controller._directory["node_2"].address == "6.7.8.9"

    def test_send_heartbeat_message(self) -> None:
        """
        Very simple test to check the correct format is being sent.
        """
        assert send_heartbeat_message("coordinator") == YES
        assert msg_url == "GET http://coordinator//heartbeat"
        assert msg_data == None
        assert msg_json == '{"name": "<hostname>", "role": "<host role>", "coordinator": null, "address": "w.x.y.z"}'

    def test_receive_heartbeat_errors_correctly(self) -> None:
        """
        Validates the heartbeat method correctly errors when the network request
        is incorrectly formed or missing data.
        """
        self.check_receive_method_conforms("/heartbeat", receive_heartbeat_message)

    def test_receive_heartbeat_message(self) -> None:
        """
        Validates the heartbeat method correctly extracts the JSON data and
        registers the node with the directory.
        """
        node_1 = MockRequest(POST, "/heartbeat", body='{"name":"node_1", "role":"role_1", "address":"1.2.3.4"}')
        node_2 = MockRequest(POST, "/heartbeat", body='{"name":"NODE_2", "role":"role_2", "address":"6.7.8.9"}')

        controller = DirectoryController()

        # Receive a heartbeat with an empty directory.
        response = receive_heartbeat_message(node_1, controller)
        assert response._body == OK
        assert response._status == OK_200
        assert len(controller._directory) == 1
        assert "node_1" in controller._directory
        assert controller._directory["node_1"].name == "node_1"
        assert controller._directory["node_1"].role == "role_1"
        assert controller._directory["node_1"].address == "1.2.3.4"
        expiry_time = controller._directory["node_1"].expiry_time

        # Receive the same heartbeat again; no change in state except time.
        time.sleep(0.1)
        response = receive_heartbeat_message(node_1, controller)
        assert response._body == OK
        assert response._status == OK_200
        assert len(controller._directory) == 1
        assert "node_1" in controller._directory
        assert controller._directory["node_1"].name == "node_1"
        assert controller._directory["node_1"].role == "role_1"
        assert controller._directory["node_1"].address == "1.2.3.4"
        assert controller._directory["node_1"].expiry_time > expiry_time

        # Receive a new heartbeat.
        response = receive_heartbeat_message(node_2, controller)
        assert response._body == OK
        assert response._status == OK_200
        assert len(controller._directory) == 2
        assert "node_1" in controller._directory
        assert controller._directory["node_1"].name == "node_1"
        assert controller._directory["node_1"].role == "role_1"
        assert controller._directory["node_1"].address == "1.2.3.4"
        assert "node_2" in controller._directory
        assert controller._directory["node_2"].name == "node_2"
        assert controller._directory["node_2"].role == "role_2"
        assert controller._directory["node_2"].address == "6.7.8.9"
