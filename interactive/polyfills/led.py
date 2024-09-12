from interactive.environment import are_pins_available

MAX_DUTY = 65535

if are_pins_available():

    from microcontroller import Pin
    import board
    from digitalio import DigitalInOut, Direction
    import pwmio


    class LedPin:
        """
        Simple implementation of Led using PWM to control the brightness.
        """

        def __init__(self, pin: Pin):
            self.pin = pin
            self.pwm = pwmio.PWMOut(pin, frequency=1000)

        def deinit(self) -> None:
            self.pin.deinit()

        def show(self, brightness: float) -> None:
            self.pwm.duty_cycle = int(MAX_DUTY * brightness)


    def __new_led_pin(pin: Pin) -> LedPin:
        """
        Sets up a PWM controlled LED using the provided Pin.

        :param pin: The pin to use for the LED.
        """
        return LedPin(pin)


    def __onboard_led() -> DigitalInOut:
        """
        Returns the boards onboard LED as a digital on/off LED.
        """
        led = DigitalInOut(board.LED)
        led.direction = Direction.OUTPUT

        return led

else:
    class LedPin:
        """
        Stub implementation of Led for Desktop without pins. Does nothing.
        """

        def __init__(self, pin):
            pass

        def deinit(self) -> None:
            pass

        def show(self, brightness: float) -> None:
            pass


    def __new_led_pin(pin) -> LedPin:
        return LedPin(pin)


    class DigitalInOut:
        def __init__(self):
            self._value = False

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self, val):
            self._value = val


    def __onboard_led() -> DigitalInOut:
        return DigitalInOut()


def new_led_pin(pin) -> LedPin:
    """
    Returns a new LED that performs the LED processing based on
    whether the code is running in CircuitPython where a pin will be
    provided or in a desktop environment where a key will be used.

    :param pin: The pin or key to use for the button signal.
    """
    return __new_led_pin(pin)


def onboard_led() -> DigitalInOut:
    """
    Returns the onboard LED as a simple DigitalInOut that can be
    turned on or off using the value property.
    """
    return __onboard_led()
