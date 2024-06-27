from framework.environment import are_pins_available

if are_pins_available():

    import pwmio
    from microcontroller import Pin


    class Buzzer:
        """
        Buzzer is a very lightweight implementation that uses PWM to play a
        sound at a given frequency. When notes are stringed together in this
        manner, they can play an acceptable tune.
        """

        def __init__(self, pin: Pin, volume: float = 1.0):
            self._pin = pin
            self._buzzer = None
            self._volume = 0.0
            self.volume = volume

        @property
        def volume(self) -> float:
            """
            Returns the volume of the buzzer. This will be a value between 0.0 and 1.0.
            """
            return self._volume

        @volume.setter
        def volume(self, volume: float) -> None:
            """
            Allows setting of the volume of the buzzer. This should be a float value in
            the range of 0.0 to 1.0.

            :param volume: The new volume.
            """
            self._volume = max(min(volume, 1.0), 0.0)

        def play(self, frequency: int) -> None:
            """
            Play a tone at the specified frequency. This will continue to play
            until another play() or off() is called.

            :param frequency: The frequency to play.
            """
            if self._buzzer:
                self._buzzer.deinit()
                self._buzzer = None

            if frequency == 0:
                self.off()
            else:
                self._buzzer = pwmio.PWMOut(self._pin, frequency=frequency)
                self._buzzer.duty_cycle = int(self.volume * (2 ** 10))

        def off(self):
            """
            Stops the buzzer playing any sound.
            """
            if self._buzzer:
                if self._buzzer is not None:
                    self._buzzer.duty_cycle = 0
                    self._buzzer.deinit()
                self._buzzer = None


    def __new_buzzer(pin: Pin) -> Buzzer:
        return Buzzer(pin)

else:
    class Buzzer:
        """
        Stub implementation of Buzzer for Desktop without pins. Does nothing.
        """

        def __init__(self, pin, volume: float = 1.0):
            self._pin = pin
            self._volume = 0.0
            self.volume = volume

        @property
        def volume(self):
            return self._volume

        @volume.setter
        def volume(self, volume: float):
            self._volume = max(min(volume, 1.0), 0.0)

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

    :param pin: The pin or key to use for the buzzer signal.
    """
    return __new_buzzer(pin)
