from interactive.environment import are_pins_available

if are_pins_available():

    from analogio import AnalogIn
    from microcontroller import Pin


    class Microphone:
        """
        Implementation of Microphone with pins. This requires an analogue
        input pin and returns the sample value that is clamped within the
        provided range.
        """

        def __init__(self, pin, minimum: int = 0, maximum: int = 65535):
            self.mic = AnalogIn(pin)
            self.min = minimum
            self.max = maximum

        @property
        def value(self) -> int:
            """
            Returns the analogue value within the given range.
            """

            # Keep the value within the minimum and maximum range.
            value = self.mic.value
            if value < self.min:
                value = self.min
            if value > self.max:
                value = self.max

            return value


    def __new_microphone(pin: Pin) -> Microphone:
        """
        Sets up a basic microphone that receives a simple analogue value from an input pin.
        This is typical of a MAX4466 type device.

        :param pin: The pin to use for the microphone signal.
        """
        return Microphone(pin)

else:
    class Microphone:
        """
        Stub implementation of Microphone for Desktop without pins. Does nothing.
        """

        def __init__(self, pin, minimum: int = 0, maximum: int = 65535):
            self.pin = pin
            self.min = minimum
            self.max = maximum

        @property
        def value(self) -> int:
            return 0


    def __new_microphone(pin) -> Microphone:
        return Microphone(pin)


def new_microphone(pin) -> Microphone:
    """
    Returns a new Microphone that performs the microphone processing based on
    whether the code is running in CircuitPython where a pin will be provided
    or in a desktop environment where nothing will be done.

    :param pin: The pin to use for the microphone signal.
    """
    return __new_microphone(pin)
