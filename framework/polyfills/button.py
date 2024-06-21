from framework.environment import are_pins_available

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
        return Button(pin, short_duration_ms=200, long_duration_ms=2000)

else:
    class Button:
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
    Returns a new callable that perform the button processing based on
    whether the code is running in CircuitPython where a pin will be
    provided or in a desktop environment where a key will be used.

    :param pin: The pin or key to use for the button signal.
    """
    return __new_button(pin)
