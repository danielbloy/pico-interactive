import asyncio
import os

from adafruit_httpserver import GET, Request, OK_200

from interactive import configuration
from interactive import network
from interactive.network import NO, TRIGGERED
from interactive.polyfills import cpu
from test_network import validate_methods, MockRequest


class TestRoutes:
    """
    NOTE: Even though these tests all specify (or at least try to) the correct route
          in the TestRequest(), those routes are not typically needed for the test methods
          as they expect to have been routed to correctly anyway.
    """

    def test_index_returns_index_html_with_get(self) -> None:
        """
        Validates that the index.html file is returned with no additional headers.
        """
        validate_methods({GET}, "/", network.index)

        path = os.getcwd()
        try:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            os.chdir(os.path.join(dir_path, "../.."))
            request = MockRequest(GET, "/")
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
        validate_methods({GET}, "/cpu-information", network.cpu_information)

        request = MockRequest(GET, "/cpu-information")
        response = network.cpu_information(request)
        assert response._data == cpu.info()
        assert response._status == OK_200
        assert len(response._headers) == 0

    def test_inspect(self) -> None:
        """
        Validates that the inspect web page is returned with no additional headers.
        """
        validate_methods({GET}, "/inspect", network.inspect)

        request = MockRequest(GET, "/inspect")
        response = network.inspect(request)
        assert response._body == "TODO inspect"
        assert response._status == OK_200
        assert len(response._headers) == 0

    def test_restart(self, monkeypatch) -> None:
        """
        Validates that restart returns with no additional headers. The restart
        won't actually restart a Desktop PC as the polyfill is a noop.
        """

        async def __validate_methods():
            validate_methods({GET}, "/restart", network.restart)

        asyncio.run(__validate_methods())

        restart_called_count = 0

        def test_restart_fn():
            nonlocal restart_called_count
            restart_called_count += 1

        monkeypatch.setattr(network, 'cpu_restart', test_restart_fn)

        # Create an event loop which is needed for the async restart request.
        request = MockRequest(GET, "/restart")

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
        validate_methods({GET}, "/alive", network.alive)

        request = MockRequest(GET, "/alive")
        response = network.alive(request)
        assert response._body == network.YES
        assert response._status == OK_200

    def test_name(self) -> None:
        """
        Validates that name returns with no additional headers.
        """
        validate_methods({GET}, "/name", network.name)

        request = MockRequest(GET, "/name")
        response = network.name(request)
        assert response._body == configuration.NODE_NAME
        assert response._status == OK_200

    def test_role(self) -> None:
        """
        Validates that role returns with no additional headers.
        """
        validate_methods({GET}, "/role", network.role)

        request = MockRequest(GET, "/role")
        response = network.role(request)
        assert response._body == configuration.NODE_ROLE
        assert response._status == OK_200

    def test_details(self) -> None:
        """
        Validates that the details information is returned with no additional headers.
        """
        validate_methods({GET}, "/details", network.details)

        request = MockRequest(GET, "/details")
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

        validate_methods({GET}, "/led/blink", network.led_blink)
        # this reset is required because the validate_methods() call invokes network.led_blink().
        message_called_count = 0

        request = MockRequest(GET, "/led/blink")
        response = network.led_blink(request)
        assert response._body == 'LED has blinked'
        assert response._status == OK_200
        assert len(response._headers) == 0

        assert message_called_count == 1

    def test_led_state(self, monkeypatch) -> None:
        """
        Validates the led_state() returns the desired state..
        """
        validate_methods({GET}, "/led/<state>", network.led_state, "ON")

        message_called_count = 0

        def test_message_fn(request: Request, state: str) -> str:
            nonlocal message_called_count
            message_called_count += 1
            return f'LED is {state}'

        monkeypatch.setattr(network, 'receive_led_message', test_message_fn)

        request = MockRequest(GET, "/led/<state>")
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

    def test_trigger_returns_no_when_no_trigger_defined(self):
        """
        Validates that the trigger returns NO when no trigger defined.
        """
        validate_methods({GET}, "/trigger", network.trigger, None)

        request = MockRequest(GET, "/trigger")
        response = network.trigger(request, None)
        assert response._body == NO
        assert response._status == OK_200
        assert len(response._headers) == 0

    def test_trigger_returns_ok_when_trigger_defined(self):
        """
        Validates that the trigger returns ok and the trigger is called when
        a trigger is defined.
        """
        callback_called_count = 0

        def callback() -> None:
            nonlocal callback_called_count
            callback_called_count += 1

        validate_methods({GET}, "/trigger", network.trigger, callback)
        assert callback_called_count == 1

        request = MockRequest(GET, "/trigger")
        response = network.trigger(request, callback)
        assert response._body == TRIGGERED
        assert response._status == OK_200
        assert len(response._headers) == 0
        assert callback_called_count == 2


class TestMessages:

    def test_receive_blink_message(self, monkeypatch) -> None:
        """
        Validates that the onboard LED is blinked regardless of its starting state.
        """

        class TestLed:
            def __init__(self):
                self._value = False
                self.values = []

            @property
            def value(self):
                return self._value

            @value.setter
            def value(self, val):
                self._value = val
                self.values.append(val)

        test_led = TestLed()
        monkeypatch.setattr(network, 'onboard_led', test_led)

        async def __execute():
            # Before calling the request, there should only be a single
            # async task which is this one.
            assert len(asyncio.all_tasks()) == 1

            # Validate when the LED starts as off.
            response = network.receive_blink_message(None)
            assert response == 'LED has blinked'

            # There should now be 2 tasks, this one and the restart async task.
            assert len(asyncio.all_tasks()) == 2

            # Await for long enough for the restart to get executed.
            while len(asyncio.all_tasks()) > 1:
                await asyncio.sleep(0.1)

            assert len(test_led.values) == 2
            assert test_led.values == [True, False]

            # Validate when the LED starts as ON.
            test_led.value = True
            test_led.values = []

            response = network.receive_blink_message(None)
            assert response == 'LED has blinked'

            # There should now be 2 tasks, this one and the restart async task.
            assert len(asyncio.all_tasks()) == 2

            # Await for long enough for the restart to get executed.
            while len(asyncio.all_tasks()) > 1:
                await asyncio.sleep(0.1)

            assert len(test_led.values) == 2
            assert test_led.values == [False, True]

        asyncio.run(__execute())

    def test_receive_led_message(self) -> None:
        """
        Validates that receive_led_message() correctly sets the state of the onboard LED.
        """
        # Unknown state should do nothing with the LED
        network.onboard_led.value = False
        response = network.receive_led_message(None, "UNKNOWN")
        assert response == 'UNKNOWN is unknown'
        assert not network.onboard_led.value

        network.onboard_led.value = True
        response = network.receive_led_message(None, "UNKNOWN")
        assert response == 'UNKNOWN is unknown'
        assert network.onboard_led.value

        # OFF should turn the LED off, regardless of the starting state
        network.onboard_led.value = False
        response = network.receive_led_message(None, network.OFF)
        assert response == 'LED is OFF'
        assert not network.onboard_led.value

        network.onboard_led.value = True
        response = network.receive_led_message(None, network.OFF)
        assert response == 'LED is OFF'
        assert not network.onboard_led.value

        # ON should turn the LED ON, regardless of the starting state
        network.onboard_led.value = False
        response = network.receive_led_message(None, network.ON)
        assert response == 'LED is ON'
        assert network.onboard_led.value

        network.onboard_led.value = True
        response = network.receive_led_message(None, network.ON)
        assert response == 'LED is ON'
        assert network.onboard_led.value
