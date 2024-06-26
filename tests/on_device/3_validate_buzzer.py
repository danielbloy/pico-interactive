import time

from framework.button import ButtonController
from framework.buzzer import BuzzerController
from framework.environment import are_pins_available
from framework.log import set_log_level, INFO
from framework.polyfills.button import new_button
from framework.polyfills.buzzer import new_buzzer
from framework.runner import Runner

BUTTON_PIN = None
BUZZER_PIN = None

if are_pins_available():
    import board

    BUTTON_PIN = board.GP27
    BUZZER_PIN = board.GP2

if __name__ == '__main__':
    # Allow the application to only run for a defined number of seconds.
    start = time.monotonic()
    finish = start + 10

    set_log_level(INFO)


    async def callback() -> None:
        global start, finish
        runner.cancel = time.monotonic() > finish
        if runner.cancel:
            buzzer_controller.off()


    async def single_click_handler() -> None:
        # Make an annoying beep
        buzzer_controller.play(262, 0.5)


    async def multi_click_handler() -> None:
        # TODO: Play song
        pass


    async def long_press_handler() -> None:
        # TODO: Stop playing song
        pass


    runner = Runner()

    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_click_handler(single_click_handler)
    button_controller.add_multi_click_handler(multi_click_handler)
    button_controller.add_long_press_handler(long_press_handler)
    button_controller.register(runner)

    buzzer = new_buzzer(BUZZER_PIN)
    buzzer_controller = BuzzerController(buzzer)
    buzzer_controller.register(runner)

    runner.run(callback)
