import time

from interactive.audio import AudioController
from interactive.button import ButtonController
from interactive.environment import are_pins_available, is_running_on_microcontroller
from interactive.log import set_log_level, info, INFO
from interactive.memory import report_memory_usage_and_free
from interactive.polyfills.audio import new_mp3_player
from interactive.polyfills.button import new_button
from interactive.runner import Runner

REPORT_RAM = is_running_on_microcontroller()

BUTTON_PIN = None

AUDIO_PIN = None
AUDIO_FILE = "lion.mp3"

if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    BUTTON_PIN = board.GP27

    AUDIO_PIN = board.GP3

if __name__ == '__main__':

    set_log_level(INFO)

    if REPORT_RAM:
        report_memory_usage_and_free("Before creating Objects")


    async def single_click_handler() -> None:
        info('Single click!')
        audio_controller.queue(AUDIO_FILE)


    runner = Runner()

    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_press_handler(single_click_handler)
    button_controller.register(runner)

    audio = new_mp3_player(AUDIO_PIN, AUDIO_FILE)
    audio_controller = AudioController(audio)
    audio_controller.register(runner)

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + 10


    async def callback() -> None:
        runner.cancel = time.monotonic() > finish


    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    runner.run(callback)

    if REPORT_RAM:
        report_memory_usage_and_free("After running Runner")
