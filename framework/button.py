import asyncio

from framework.environment import is_running_on_desktop
from framework.runner import Runner

# collections.abc is not available in CircuitPython.
if is_running_on_desktop():
    from collections.abc import Callable, Awaitable


class Button:
    """
    TODO: Comments
    """

    def __init__(self):
        self.__running = False
        self.__single_click_handler = None
        self.__double_click_handler = None
        self.__long_press_handler = None

    def add_single_click_handler(self, handler: Callable[[], Awaitable[None]] = None):
        self.__single_click_handler = handler

    def add_double_click_handler(self, handler: Callable[[], Awaitable[None]] = None):
        self.__double_click_handler = handler

    def add_long_press_handler(self, handler: Callable[[], Awaitable[None]] = None):
        self.__long_press_click_handler = handler

    def register(self, runner: Runner) -> None:
        """
        TODO: Comments: Register with runner.
        :param runner:
        :return:
        """
        runner.add_task(self.__loop)

    async def __loop(self) -> None:
        while True:
            # TODO: Call the polyfill to handle the actual button signals.
            await asyncio.sleep(0.1)
