from framework.environment import is_running_on_desktop
from framework.polyfills.button import new_button
from framework.runner import Runner

# collections.abc is not available in CircuitPython.
if is_running_on_desktop():
    from collections.abc import Callable, Awaitable


class Button:
    """
    TODO: Comments
    """

    def __init__(self, pin):
        self.__running = False
        self.__single_click_handler = None
        self.__double_click_handler = None
        self.__long_press_handler = None
        self.__pin = pin
        self.__button = new_button(pin, self.__handler)

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
        runner.add_task(self.__button)

    async def __handler(self):
        print("handler called")
        # This needs to work out whether it is a single click, double click or long click.
        # TODO: The handler will probably need to receive the rise and fall
        pass
