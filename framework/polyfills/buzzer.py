from framework.environment import are_pins_available

if are_pins_available():

    import pwmio
    from microcontroller import Pin


    class Buzzer:
        def __init__(self, pin: Pin, volume=1.0):
            self._pin = pin
            self._buzzer = None
            self._volume = volume

        @property
        def volume(self):
            return self._volume

        @volume.setter
        def volume(self, volume):
            self._volume = volume

        def play(self, frequency: int):
            if self._buzzer:
                self._buzzer.deinit()
                self._buzzer = None

            if frequency == 0:
                self.off()
            else:
                self._buzzer = pwmio.PWMOut(self._pin, frequency=frequency)
                self._buzzer.duty_cycle = int(self.volume * (2 ** 10))

        def off(self):
            if self._buzzer:
                if self._buzzer is not None:
                    self._buzzer.duty_cycle = 0
                    self._buzzer.deinit()
                self._buzzer = None


    def __new_button(pin: Pin) -> Buzzer:
        return Buzzer(pin)

else:
    class Buzzer:
        """
        TODO: Implement a Buzzer that works on a desktop.
        """

        def __init__(self, pin, volume=1.0):
            pass

        @property
        def volume(self):
            return 0

        @volume.setter
        def volume(self, volume):
            pass

        def play(self, frequency: int):
            pass

        def off(self):
            pass


    def __new_buzzer(pin) -> Buzzer:
        return Buzzer(pin)


def new_buzzer(pin) -> Buzzer:
    """
    Returns a new Buzzer that perform the buzzer processing based on
    whether the code is running in CircuitPython where a pin will be
    provided or in a desktop environment where a key will be used.

    :param pin: The pin or key to use for the button signal.
    """
    return __new_buzzer(pin)
