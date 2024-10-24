import time

from interactive.button import ButtonController
from interactive.environment import are_pins_available, is_running_on_microcontroller
from interactive.log import set_log_level, info, INFO
from interactive.memory import report_memory_usage_and_free
from interactive.polyfills.button import new_button
from interactive.polyfills.led import onboard_led
from interactive.runner import Runner

REPORT_RAM = is_running_on_microcontroller()

BUTTON_PIN = None

if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    BUTTON_PIN = board.GP27

if __name__ == '__main__':

    set_log_level(INFO)

    if REPORT_RAM:
        report_memory_usage_and_free("Before creating Objects")

    led = onboard_led()


    async def single_click_handler() -> None:
        info('Single click!')
        led.value = not led.value


    async def multi_click_handler() -> None:
        info('Multi click!')


    async def long_press_handler() -> None:
        info('Long press!')


    runner = Runner()

    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_press_handler(single_click_handler)
    button_controller.add_multi_press_handler(multi_click_handler)
    button_controller.add_long_press_handler(long_press_handler)
    button_controller.register(runner)

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + 10


    async def callback() -> None:
        runner.cancel = time.monotonic() > finish


    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    runner.run(callback)

    if REPORT_RAM:
        report_memory_usage_and_free("After running Runner")
