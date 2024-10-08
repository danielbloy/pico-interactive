from collections.abc import Callable

import pytest
from adafruit_httpserver import GET, POST, NOT_IMPLEMENTED_501, PUT, OK_200, Request, BAD_REQUEST_400
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
        json_body = '{"name":"daniel", "role":"programmer", "ip":"a.b.c.d"}'
        # When there is a coordinator nothing should error; except when there is no directory specified.
        monkeypatch.setattr(network, 'NODE_COORDINATOR', "node")
        validate_methods({GET, POST, PUT}, route, func, DirectoryController())

        # Should always error if no directory controller is specified.
        with pytest.raises(ValueError):
            func(MockRequest(GET, route, body=json_body), None)

        func(MockRequest(GET, route, body=json_body), DirectoryController())
        func(MockRequest(PUT, route, body=json_body), DirectoryController())
        func(MockRequest(POST, route, body=json_body), DirectoryController())

        # When there is no coordinator should error but only if it is a POST or PUT
        monkeypatch.setattr(network, 'NODE_COORDINATOR', None)

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
        self.check_directory_method_conforms(monkeypatch, "/register", network.register)

    def test_register(self, monkeypatch) -> None:
        """
        Validates that the register message responds to GET, PUT and POST requests
        along with the required validation and that the correct message handling functions
        are called; this assumes success each time.
        """
        monkeypatch.setattr(network, 'NODE_COORDINATOR', "node")

        controller = DirectoryController()

        validate_methods({GET, POST, PUT}, "/register", network.register, controller)

        # This registers the node with the coordinator; we validate the message is sent.
        request = MockRequest(GET, "/register")
        response = network.register(request, controller)
        assert response._body == 'registered with coordinator'
        assert response._status == OK_200

        # TODO: Validate that the message is sent and a valid response is returned.
        assert len(controller._directory) == 0

        # TODO: Validate that a new item was registered
        request = MockRequest(POST, "/register")
        response = network.register(request, controller)
        assert response._body == network.OK
        assert response._status == OK_200

        # TODO: Lookup name as well
        assert len(controller._directory) == 1

        # TODO: Validate that a second item was registered
        request = MockRequest(POST, "/register")
        response = network.register(request, controller)
        assert response._body == network.OK
        assert response._status == OK_200

        # TODO: Lookup name as well
        assert len(controller._directory) == 2

        # TODO: Validate that the first item was registered, but this time updated.
        request = MockRequest(PUT, "/register")
        response = network.register(request, controller)
        assert response._body == network.OK
        assert response._status == OK_200

        # TODO: Lookup name as well
        assert len(controller._directory) == 2

    def test_unregister_errors_correctly(self, monkeypatch) -> None:
        """
        Runs the basic validation checks expected of the three main directory methods.
        """
        self.check_directory_method_conforms(monkeypatch, "/unregister", network.unregister)

    def test_unregister(self, monkeypatch) -> None:
        """
        Validates that the unregister message responds to GET, PUT and POST requests
        along with the required validation and that the correct message handling functions
        are called; this assumes success each time.
        """
        monkeypatch.setattr(network, 'NODE_COORDINATOR', "node")

        controller = DirectoryController()

        validate_methods({GET, POST, PUT}, "/unregister", network.unregister, controller)

        request = MockRequest(GET, "/unregister")
        response = network.unregister(request, controller)
        assert response._body == 'unregistered from coordinator'
        assert response._status == OK_200

        # TODO: Validate that the message is sent and a valid response is returned.
        assert len(controller._directory) == 0

        # TODO: Validate unregister from an empty directory
        request = MockRequest(POST, "/unregister")
        response = network.unregister(request, controller)
        assert response._body == network.OK
        assert response._status == OK_200

        assert len(controller._directory) == 0

        # Add some entries
        controller.register_endpoint("a.b.c.d", "node1", "role1")
        controller.register_endpoint("1.2.3.4", "node2", "role2")
        assert len(controller._directory) == 2

        # TODO: Unregister an unknown endpoint
        request = MockRequest(PUT, "/unregister")
        response = network.unregister(request, controller)
        assert response._body == network.OK
        assert response._status == OK_200

        assert len(controller._directory) == 2

        # TODO: Unregister unknown endpoint
        request = MockRequest(PUT, "/unregister")
        response = network.unregister(request, controller)
        assert response._body == network.OK
        assert response._status == OK_200

        # TODO: Lookup the other name to validate the correct item was removed.
        assert len(controller._directory) == 1

        # TODO: Unregister the same  endpoint
        request = MockRequest(PUT, "/unregister")
        response = network.unregister(request, controller)
        assert response._body == network.OK
        assert response._status == OK_200

        assert len(controller._directory) == 1

    def test_heartbeat_errors_correctly(self, monkeypatch) -> None:
        """
        Runs the basic validation checks expected of the three main directory methods.
        """
        self.check_directory_method_conforms(monkeypatch, "/heartbeat", network.heartbeat)

    def test_heartbeat(self, monkeypatch) -> None:
        """
        Validates that the heartbeat message responds to GET, PUT and POST requests
        along with the required validation and that the correct message handling functions
        are called; this assumes success each time.
        """
        monkeypatch.setattr(network, 'NODE_COORDINATOR', "node")

        controller = DirectoryController()

        validate_methods({GET, POST, PUT}, "/heartbeat", network.heartbeat, controller)

        request = MockRequest(GET, "/heartbeat")
        response = network.heartbeat(request, controller)
        assert response._body == 'heartbeat message sent to coordinator'
        assert response._status == OK_200

        # TODO: Validate that the message is sent and a valid response is returned.
        assert len(controller._directory) == 0

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
        response = func(MockRequest(POST, route, body='{"ip":"i", "role":"r"}'), DirectoryController())
        assert response._body == "NO_NAME_SPECIFIED"
        assert response._status == BAD_REQUEST_400

        # Might error if no address is provided in the body
        response = func(MockRequest(POST, route, body='{"name":"n", "role":"r"}'), DirectoryController())
        if requires_address:
            assert response._body == "NO_IP_ADDRESS_SPECIFIED"
            assert response._status == BAD_REQUEST_400
        else:
            assert response._body == network.OK
            assert response._status == OK_200

        print("a")
        # Might error if no role is provided in the body
        response = func(MockRequest(POST, route, body='{"name":"n", "ip":"i"}'), DirectoryController())
        if requires_role:
            assert response._body == "NO_ROLE_SPECIFIED"
            assert response._status == BAD_REQUEST_400
        else:
            assert response._body == network.OK
            assert response._status == OK_200

    def test_send_register_message(self) -> None:
        assert network.send_register_message(None) == "registered with coordinator"

    def test_receive_register_errors_correctly(self) -> None:
        self.check_receive_method_conforms("/register", network.receive_register_message)

    def test_receive_register_message(self) -> None:
        assert network.receive_register_message(None) == network.OK

    def test_send_unregister_message(self) -> None:
        assert network.send_unregister_message(None) == "unregistered from coordinator"

    def test_receive_unregister_errors_correctly(self) -> None:
        self.check_receive_method_conforms("/unregister", network.receive_unregister_message, False, False)

    def test_receive_unregister_message(self) -> None:
        assert network.receive_unregister_message(None) == network.OK

    def test_send_heartbeat_message(self) -> None:
        assert network.send_heartbeat_message(None) == "heartbeat message sent to coordinator"

    def test_receive_heartbeat_errors_correctly(self) -> None:
        self.check_receive_method_conforms("/heartbeat", network.receive_heartbeat_message)

    def test_receive_heartbeat_message(self) -> None:
        assert network.receive_heartbeat_message(None) == "TODO heartbeat message received from node"

# print(request)
# print(f"METHOD ... : '{request.method}'")
# print(f"PATH ..... : '{request.path}'")
# print(f"QPARAMS .. : '{request.query_params}'")
# print(f"HTTPV .... : '{request.http_version}'")
# print(f"HEADERS .. : '{request.headers}'")
# print(f"BODY ..... : '{request.body}'")
# print(f"RAW ...... : '{request.raw_request}'")
