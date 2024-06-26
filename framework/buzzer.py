import asyncio

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

    def register(self, runner: Runner) -> None:
        """
        Registers this Buzzer instance as a task with the provided Runner.

        :param runner: the runner to register with.
        """
        runner.add_task(self.__loop)

    async def __loop(self):
        """
        TODO:
        """
        while True:
            await asyncio.sleep(ASYNC_LOOP_SLEEP_INTERVAL)
            pass

# TODO: Migrate music.py/Song from originals/christmas
# TODO: Migrate music.py/SongSequence from originals/christmas
