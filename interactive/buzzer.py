import time

from interactive.control import NS_PER_SECOND
from interactive.polyfills.buzzer import Buzzer
from interactive.runner import Runner


class BuzzerController:

    def __init__(self, buzzer: Buzzer):
        if buzzer is None:
            raise ValueError("buzzer cannot be None")

        if not isinstance(buzzer, Buzzer):
            raise ValueError("buzzer must be of type Buzzer")

        self.__buzzer = buzzer
        self.__playing = False
        self.__stop_time_ns = 0
        self.__beeps = 0

    def beep(self) -> None:
        """
        Makes a beep.
        """
        self.__beeps -= 1
        self.play(262, 0.3)

    def beeps(self, count: int) -> None:
        """
        Plays a series of beeps.

        :param count: The number of beeps to play.
        """
        self.__beeps = count
        self.beep()

    def play(self, frequency: int, duration: float) -> None:
        """
        Plays a tone at the given frequency for the specified number of seconds.

        :param frequency: The frequency to play the tone at.
        :param duration: The duration in seconds to play the tone for.
        """
        # Calculate the stop time.
        self.__stop_time_ns = time.monotonic_ns() + int(duration * NS_PER_SECOND)
        self.__playing = True
        self.__buzzer.play(frequency)

    def off(self) -> None:
        """
        Turns off the buzzer; cancelling and additional beeps..
        """
        self.__beeps = 0
        self.__off()

    def __off(self) -> None:
        self.__playing = False
        self.__buzzer.off()

    def register(self, runner: Runner) -> None:
        """
        Registers this Buzzer instance as a task with the provided Runner.

        :param runner: the runner to register with.
        """
        runner.add_loop_task(self.__loop)

    async def __loop(self):
        """
        Internal loop to turn the buzzer off at the desired time internal.
        """
        if (self.__playing or self.__beeps > 0) and time.monotonic_ns() >= self.__stop_time_ns:
            if self.__playing:
                self.__off()

                # Allow for a delay between beeps.
                if self.__beeps > 0:
                    self.__stop_time_ns += (0.1 * NS_PER_SECOND)

            else:

                # If there are more beeps expected in the sequence then play them.
                if self.__beeps > 0:
                    self.beep()
