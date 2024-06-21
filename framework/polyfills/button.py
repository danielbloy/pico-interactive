from framework.environment import are_pins_available

if are_pins_available():

    import digitalio


    # from adafruit_debouncer import Button
    # Probably need to import  microcontroller.Pin

    def __new_button(pin: Pin) -> Button:
        pin = digitalio.DigitalInOut(pin)
        pin.direction = digitalio.Direction.INPUT
        pin.pull = digitalio.Pull.UP
        return Button(pin, short_duration_ms=50, long_duration_ms=200)

else:
    class Button:
        def __init__(self, pin):
            pass

        def update(self) -> None:
            pass

        @property
        def pressed(self) -> bool:
            return False  # TODO

        @property
        def released(self) -> bool:
            return False  # TODO

        @property
        def short_count(self) -> int:
            return 0  # TODO

        @property
        def long_press(self) -> bool:
            return False  # TODO


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
