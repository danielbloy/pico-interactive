from framework.environment import is_running_on_desktop
from framework.polyfills.button import Button
from framework.runner import Runner

# collections.abc is not available in CircuitPython.
if is_running_on_desktop():
    from collections.abc import Callable, Awaitable


class ButtonController:
    """
    ButtonController provides abstracted single-click, multi-click and long-press
    callbacks based on a Button interface. In CircuitPython, the button will likely
    be based on a real physical button connected to a pin whereas under a normal PC
    (without Blinka running) this could be a simple keypress.

    Instances of this class will need to register() with a Runner in order to work.
    """

    def __init__(self, button: Button):
        if button is None:
            raise ValueError("button cannot be None")

        if not isinstance(button, Button):
            raise ValueError("button must be of type Button")

        self.__button = button
        self.__single_click_handler = None
        self.__multi_click_handler = None
        self.__long_press_handler = None

    def add_single_click_handler(self, handler: Callable[[], Awaitable[None]] = None):
        """
        Adds a handler for the single-click event. Overwrites any previous handler.

        :param handler: The handler to call if a single-click event occurs.
        """
        self.__single_click_handler = handler

    def add_multi_click_handler(self, handler: Callable[[], Awaitable[None]] = None):
        """
        Adds a handler for the multi-click event. Overwrites any previous handler.

        :param handler: The handler to call if a multi-click event occurs.
        """
        self.__multi_click_handler = handler

    def add_long_press_handler(self, handler: Callable[[], Awaitable[None]] = None):
        """
        Adds a handler for the long-press event. Overwrites any previous handler.

        :param handler: The handler to call if a long-press event occurs.
        """
        self.__long_press_handler = handler

    def register(self, runner: Runner) -> None:
        """
        Registers this Button instance as a task with the provided Runner.

        :param runner: the runner to register with.
        """
        runner.add_loop_task(self.__loop)

    async def __loop(self):
        """
        The internal loop simply invokes the correct handler based on the button state.
        """
        self.__button.update()

        short_count = self.__button.short_count
        if short_count != 0:

            if short_count == 1 and self.__single_click_handler is not None:
                await self.__single_click_handler()

            elif short_count > 1 and self.__multi_click_handler is not None:
                await self.__multi_click_handler()

        if self.__button.long_press and self.__long_press_handler is not None:
            await self.__long_press_handler()
