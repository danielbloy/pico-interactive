import asyncio

from framework.environment import is_running_on_desktop
from framework.polyfills.button import Button
from framework.runner import Runner

# collections.abc is not available in CircuitPython.
if is_running_on_desktop():
    from collections.abc import Callable, Awaitable

# TODO: extract this out
SLEEP_INTERVAL = 0.1


class ButtonController:
    """
    ButtonController provides abstracted single-click, double-click and long-press
    callbacks based on a Button interface. In CircuitPython, the button will likely
    be based on a real physical button connected to a pin whereas under a normal PC
    (without Blinka running) this would be a simple keypress. Testing can provide
    its own implementation to validate behaviour.
    """

    def __init__(self, button: Button):
        self.__running = False
        self.__single_click_handler = None
        self.__double_click_handler = None
        self.__long_press_handler = None
        self.__button = button

    def add_single_click_handler(self, handler: Callable[[], Awaitable[None]] = None):
        self.__single_click_handler = handler

    def add_double_click_handler(self, handler: Callable[[], Awaitable[None]] = None):
        self.__double_click_handler = handler

    def add_long_press_handler(self, handler: Callable[[], Awaitable[None]] = None):
        self.__long_press_handler = handler

    def register(self, runner: Runner) -> None:
        """
        Registers this Button instance as a task with the provided Runner.
        :param runner: the runner to register with.
        """

        runner.add_task(self.__loop)

    async def __loop(self):
        while True:
            await asyncio.sleep(SLEEP_INTERVAL / 1000)  # TODO: Better calculated interval.
            self.__button.update()

            # TODO: Remove
            print(self.__button.short_count, self.__button.long_press)

            # This needs to work out whether it is a single click, double click or long click.
