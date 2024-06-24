import time

from framework.button import ButtonController
from framework.buzzer import BuzzerController
from framework.environment import are_pins_available
from framework.log import set_log_level, INFO
from framework.polyfills.button import new_button
from framework.polyfills.buzzer import new_buzzer
from framework.runner import Runner

BUTTON_PIN = " "

if are_pins_available():
    import board

    BUTTON_PIN = board.GP27
    BUZZER_PIN = board.GP28

if __name__ == '__main__':
    # Allow the application to only run for a defined number of seconds.
    start = time.monotonic()
    finish = start + 10

    set_log_level(INFO)


    async def callback() -> None:
        global start, finish
        runner.cancel = time.monotonic() > finish


    async def single_click_handler() -> None:
        # TODO: Pause/Unpause
        pass


    async def multi_click_handler() -> None:
        # TODO: Next song
        pass


    async def long_press_handler() -> None:
        # TODO: Restart song
        pass


    runner = Runner()

    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_click_handler(single_click_handler)
    button_controller.add_multi_click_handler(multi_click_handler)
    button_controller.add_long_press_handler(long_press_handler)
    button_controller.register(runner)

    buzzer = new_buzzer(BUZZER_PIN)
    buzzer_controller = BuzzerController(button)
    buzzer_controller.register(runner)

    runner.run(callback)
