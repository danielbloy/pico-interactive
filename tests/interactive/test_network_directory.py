import pytest
from adafruit_httpserver import GET, POST, NOT_IMPLEMENTED_501, PUT

import network
from test_network import mock_send_message, validate_methods, TestRequest


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
        validate_methods({GET, POST, PUT}, "/register", network.register)
        # TODO: Write the rest of the tests

    def test_unregister(self) -> None:
        validate_methods({GET, POST, PUT}, "/unregister", network.unregister)
        # TODO: Write the rest of the tests

    def test_heartbeat(self) -> None:
        validate_methods({GET, POST, PUT}, "/heartbeat", network.heartbeat)
        # TODO: Write the rest of the tests

    def test_lookup_all(self) -> None:
        """
        Validates that lookup_all() returns NOT_IMPLEMENTED_501 with no additional headers.
        """
        validate_methods({GET}, "/lookup/all", network.lookup_all)

        request = TestRequest(GET, "/lookup/all")
        response = network.lookup_all(request)
        assert response._body == network.NO
        assert response._status == NOT_IMPLEMENTED_501

    def test_lookup_name(self) -> None:
        """
        Validates that lookup_name() returns NOT_IMPLEMENTED_501 with no additional headers.
        """
        validate_methods({GET}, "/lookup/name/<name>", network.lookup_name, "NAME")

        request = TestRequest(GET, "/lookup/name/<name>")
        response = network.lookup_name(request, "")
        assert response._body == network.NO
        assert response._status == NOT_IMPLEMENTED_501

    def test_lookup_role(self) -> None:
        """
        Validates that lookup_role() returns NOT_IMPLEMENTED_501 with no additional headers.
        """
        validate_methods({GET}, "/lookup/role/<role>", network.lookup_role, "ROLE")

        request = TestRequest(GET, "/lookup/role/<role>")
        response = network.lookup_role(request, "")
        assert response._body == network.NO
        assert response._status == NOT_IMPLEMENTED_501


class TestMessages:

    @pytest.fixture(autouse=True)
    def send_message_patched(self, monkeypatch):
        monkeypatch.setattr(network, 'send_message', mock_send_message)

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
