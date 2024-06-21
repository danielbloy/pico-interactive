import time

from framework.button import ButtonController
from framework.environment import are_pins_available
from framework.polyfills.button import new_button
from framework.runner import Runner

BUTTON_PIN = " "

if are_pins_available():
    import board

    BUTTON_PIN = board.GP27

if __name__ == '__main__':
    # Allow the application to only run for a defined number of seconds.
    start = time.monotonic()
    finish = start + 10


    async def callback() -> None:
        global start, finish
        runner.cancel = time.monotonic() > finish


    async def single_click_handler() -> None:
        print('Single click!')


    async def multi_click_handler() -> None:
        print('Multi click!')


    async def long_press_handler() -> None:
        print('Long press!')


    runner = Runner()
    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_click_handler(single_click_handler)
    button_controller.add_multi_click_handler(multi_click_handler)
    button_controller.add_long_press_handler(long_press_handler)
    button_controller.register(runner)
    runner.run(callback)
