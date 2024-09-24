# Test demonstration code for the single microcontroller board. Tests:
# * Button - triggers sound when pressed
# * Ultrasonic sensor - triggers sound when detects
# * Audio - plays lion.mp3

import time

from interactive.audio import AudioController
from interactive.button import ButtonController
from interactive.environment import are_pins_available
from interactive.log import set_log_level, INFO, info
from interactive.memory import report_memory_usage_and_free
from interactive.polyfills.audio import new_mp3_player
from interactive.polyfills.button import new_button
from interactive.polyfills.ultrasonic import new_ultrasonic
from interactive.runner import Runner
from interactive.ultrasonic import UltrasonicController

REPORT_RAM = are_pins_available()

BUTTON_PIN = None

AUDIO_PIN = None
AUDIO_FILE = "lion.mp3"

ULTRASONIC_TRIGGER_PIN = None
ULTRASONIC_ECHO_PIN = None

if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    BUTTON_PIN = board.GP26

    ULTRASONIC_TRIGGER_PIN = board.GP16
    ULTRASONIC_ECHO_PIN = board.GP17

    AUDIO_PIN = board.GP22

if __name__ == '__main__':

    set_log_level(INFO)

    if REPORT_RAM:
        report_memory_usage_and_free("Before creating Objects")

    runner = Runner()

    ultrasonic = new_ultrasonic(ULTRASONIC_TRIGGER_PIN, ULTRASONIC_ECHO_PIN)


    async def trigger_handler(distance: float, actual: float) -> None:
        info(f"Distance {distance} handler triggered: {actual}")
        audio_controller.queue(AUDIO_FILE)


    controller = UltrasonicController(ultrasonic)
    controller.add_trigger(100, trigger_handler, 5)
    controller.register(runner)


    async def single_click_handler() -> None:
        info(f"Distance: {ultrasonic.distance}")
        audio_controller.queue(AUDIO_FILE)


    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_press_handler(single_click_handler)
    button_controller.register(runner)

    audio = new_mp3_player(AUDIO_PIN, AUDIO_FILE)
    audio_controller = AudioController(audio)
    audio_controller.register(runner)

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + 1200


    async def callback() -> None:
        runner.cancel = time.monotonic() > finish


    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    runner.run(callback)

    if REPORT_RAM:
        report_memory_usage_and_free("After running Runner")
