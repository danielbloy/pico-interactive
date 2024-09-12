import pytest
from adafruit_httpserver import GET, POST, NOT_IMPLEMENTED_501, PUT, OK_200

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

    def test_register(self) -> None:
        """
        Temporary tests awaiting full implementation of directory service.
        """
        validate_methods({GET, POST, PUT}, "/register", network.register)

        request = MockRequest(GET, "/register")
        response = network.register(request)
        assert response._body == 'registered with coordinator'
        assert response._status == OK_200

        request = MockRequest(POST, "/register")
        response = network.register(request)
        assert response._body == network.OK
        assert response._status == OK_200

        request = MockRequest(PUT, "/register")
        response = network.register(request)
        assert response._body == network.OK
        assert response._status == OK_200

    def test_unregister(self) -> None:
        """
        Temporary tests awaiting full implementation of directory service.
        """
        validate_methods({GET, POST, PUT}, "/unregister", network.unregister)

        request = MockRequest(GET, "/unregister")
        response = network.unregister(request)
        assert response._body == 'unregistered from coordinator'
        assert response._status == OK_200

        request = MockRequest(POST, "/unregister")
        response = network.unregister(request)
        assert response._body == network.OK
        assert response._status == OK_200

        request = MockRequest(PUT, "/unregister")
        response = network.unregister(request)
        assert response._body == network.OK
        assert response._status == OK_200

    def test_heartbeat(self) -> None:
        """
        Temporary tests awaiting full implementation of directory service.
        """
        validate_methods({GET, POST, PUT}, "/heartbeat", network.heartbeat)

        request = MockRequest(GET, "/heartbeat")
        response = network.heartbeat(request)
        assert response._body == 'heartbeat message sent to coordinator'
        assert response._status == OK_200

        request = MockRequest(POST, "/heartbeat")
        response = network.heartbeat(request)
        assert response._body == 'TODO heartbeat message received from node'
        assert response._status == OK_200

        request = MockRequest(PUT, "/heartbeat")
        response = network.heartbeat(request)
        assert response._body == 'TODO heartbeat message received from node'
        assert response._status == OK_200

    def test_lookup_all(self) -> None:
        """
        Validates that lookup_all() returns NOT_IMPLEMENTED_501 with no additional headers.
        """
        validate_methods({GET}, "/lookup/all", network.lookup_all)

        request = MockRequest(GET, "/lookup/all")
        response = network.lookup_all(request)
        assert response._body == network.NO
        assert response._status == NOT_IMPLEMENTED_501

    def test_lookup_name(self) -> None:
        """
        Validates that lookup_name() returns NOT_IMPLEMENTED_501 with no additional headers.
        """
        validate_methods({GET}, "/lookup/name/<name>", network.lookup_name, "NAME")

        request = MockRequest(GET, "/lookup/name/<name>")
        response = network.lookup_name(request, "")
        assert response._body == network.NO
        assert response._status == NOT_IMPLEMENTED_501

    def test_lookup_role(self) -> None:
        """
        Validates that lookup_role() returns NOT_IMPLEMENTED_501 with no additional headers.
        """
        validate_methods({GET}, "/lookup/role/<role>", network.lookup_role, "ROLE")

        request = MockRequest(GET, "/lookup/role/<role>")
        response = network.lookup_role(request, "")
        assert response._body == network.NO
        assert response._status == NOT_IMPLEMENTED_501


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
