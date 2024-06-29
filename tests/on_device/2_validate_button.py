import time

from interactive.button import ButtonController
from interactive.environment import are_pins_available
from interactive.log import set_log_level, info, INFO
from interactive.polyfills.button import new_button
from interactive.runner import Runner

BUTTON_PIN = None

if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    BUTTON_PIN = board.GP27

if __name__ == '__main__':
    # Allow the application to only run for a defined number of seconds.
    start = time.monotonic()
    finish = start + 10

    set_log_level(INFO)


    async def callback() -> None:
        global start, finish
        runner.cancel = time.monotonic() > finish


    async def single_click_handler() -> None:
        info('Single click!')


    async def multi_click_handler() -> None:
        info('Multi click!')


    async def long_press_handler() -> None:
        info('Long press!')


    runner = Runner()
    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_click_handler(single_click_handler)
    button_controller.add_multi_click_handler(multi_click_handler)
    button_controller.add_long_press_handler(long_press_handler)
    button_controller.register(runner)
    runner.run(callback)
