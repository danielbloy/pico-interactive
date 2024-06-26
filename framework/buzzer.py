import asyncio
import time

from framework.control import ASYNC_LOOP_SLEEP_INTERVAL
from framework.polyfills.buzzer import Buzzer
from framework.runner import Runner


class BuzzerController:

    def __init__(self, buzzer: Buzzer):
        if buzzer is None:
            raise ValueError("buzzer cannot be None")

        if not isinstance(buzzer, Buzzer):
            raise ValueError("buzzer must be of type Buzzer")

        self.__buzzer = buzzer
        self.__playing = False
        self.__stop_time_ns = 0

    def register(self, runner: Runner) -> None:
        """
        Registers this Buzzer instance as a task with the provided Runner.

        :param runner: the runner to register with.
        """
        runner.add_task(self.__loop)

    def play(self, frequency: int, duration: float) -> None:
        """
        Plays a tone at the given frequency for the specified number of seconds.

        :param frequency: The frequency to play the tone at.
        :param duration: The duration in seconds to play the tone for.
        """
        # Calculate the stop time.
        self.__stop_time_ns = time.monotonic_ns() + int(duration * 1_000_000_000)
        self.__playing = True
        self.__buzzer.play(frequency)

    def off(self):
        """
        Turns off the buzzer.
        """
        self.__playing = False
        self.__buzzer.off()

    async def __loop(self):
        """
        Internal loop to turn the buzzer off at the desired time internal.
        """
        while True:
            await asyncio.sleep(ASYNC_LOOP_SLEEP_INTERVAL)
            if self.__playing and time.monotonic_ns() >= self.__stop_time_ns:
                self.off()
