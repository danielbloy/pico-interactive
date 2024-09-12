# Tests running the following pico interactive components together
# on a single microcontroller to check RAM and space limits:
#  * Runner
#  * Button
#  * Audio
#  * Pixels
#
import time

from interactive.animation import Flicker
from interactive.audio import AudioController
from interactive.button import ButtonController
from interactive.environment import are_pins_available, is_running_on_microcontroller
from interactive.log import set_log_level, INFO, critical
from interactive.memory import report_memory_usage_and_free
from interactive.polyfills.animation import ORANGE, BLACK
from interactive.polyfills.audio import new_mp3_player
from interactive.polyfills.button import new_button
from interactive.polyfills.pixel import new_pixels
from interactive.runner import Runner

REPORT_RAM = is_running_on_microcontroller()
REPORT_RAM_PERIODIC = REPORT_RAM and True
REPORT_RAM_PERIOD = 5

BUTTON_PIN = None

AUDIO_PIN = None
AUDIO_FILE = "lion.mp3"

PIXEL_BRIGHTNESS = 1.0
PIXEL_OFF = 0.0
PIXEL_SPEED = 0.1
PIXEL_COLOUR = ORANGE
PIXEL_PINS = []

if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    BUTTON_PIN = board.GP27

    AUDIO_PIN = board.GP3

    PIXEL_PINS = [board.GP10, board.GP11, board.GP12, board.GP13, board.GP14, board.GP15]

if __name__ == '__main__':

    set_log_level(INFO)

    if REPORT_RAM:
        report_memory_usage_and_free("Before creating Objects")


    async def single_click_handler() -> None:
        critical('Single click!')
        audio_controller.queue(AUDIO_FILE)


    runner = Runner()

    if REPORT_RAM_PERIODIC:
        async def report_memory() -> None:
            from interactive.memory import report_memory_usage
            report_memory_usage("Periodic report RAM")


        from interactive.scheduler import TriggerableAlwaysOn, new_triggered_task, terminate_on_cancel

        triggerable = TriggerableAlwaysOn()
        report_memory_task = (
            new_triggered_task(
                triggerable, REPORT_RAM_PERIOD, start=report_memory,
                cancel_func=terminate_on_cancel(runner)))
        runner.add_task(report_memory_task)

    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_click_handler(single_click_handler)
    button_controller.register(runner)

    audio = new_mp3_player(AUDIO_PIN, AUDIO_FILE)
    audio_controller = AudioController(audio)
    audio_controller.register(runner)

    pixels = [new_pixels(pin, 8, brightness=PIXEL_BRIGHTNESS) for pin in PIXEL_PINS if pin is not None]
    animations = [Flicker(pixel, speed=PIXEL_SPEED, color=PIXEL_COLOUR) for pixel in pixels]


    async def animate_pixels() -> None:
        if not runner.cancel:
            for animation in animations:
                animation.animate()


    runner.add_loop_task(animate_pixels)

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + 10


    async def callback() -> None:
        runner.cancel = time.monotonic() > finish
        if runner.cancel:
            for animation in animations:
                animation.freeze()

            for pixel in pixels:
                pixel.fill(BLACK)
                pixel.write()


    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    runner.run(callback)

    if REPORT_RAM:
        report_memory_usage_and_free("After running Runner")
