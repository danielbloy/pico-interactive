from interactive.control import BUTTON_SHORT_DURATION_MS, BUTTON_LONG_DURATION_MS
from interactive.environment import are_pins_available

if are_pins_available():

    import digitalio

    from adafruit_debouncer import Button
    from microcontroller import Pin


    def __new_button(pin: Pin) -> Button:
        """
        Sets up a debounced Button using the provided Pin. All the heavy lifting
        is done by CircuitPython.

        :param pin: The pin to use for the button.
        """
        pin = digitalio.DigitalInOut(pin)
        pin.direction = digitalio.Direction.INPUT
        pin.pull = digitalio.Pull.UP
        return Button(pin, short_duration_ms=BUTTON_SHORT_DURATION_MS, long_duration_ms=BUTTON_LONG_DURATION_MS)

else:
    class Button:
        """
        Stub implementation of Button for Desktop without pins. Does nothing.
        """

        def __init__(self, pin):
            pass

        def update(self) -> None:
            pass

        @property
        def pressed(self) -> bool:
            return False

        @property
        def released(self) -> bool:
            return False

        @property
        def short_count(self) -> int:
            return 0

        @property
        def long_press(self) -> bool:
            return False


    def __new_button(pin) -> Button:
        return Button(pin)


def new_button(pin) -> Button:
    """
    Returns a new Button that performs the button processing based on
    whether the code is running in CircuitPython where a pin will be
    provided or in a desktop environment where nothing will be done.

    :param pin: The pin to use for the button signal.
    """
    return __new_button(pin)
