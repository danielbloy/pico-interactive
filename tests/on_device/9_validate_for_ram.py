# This runs the full pico interactive framework with everything turned on to allow for
# testing RAM usage.
import time

from interactive.animation import Flicker
from interactive.configuration import get_node_config
from interactive.environment import are_pins_available
from interactive.interactive import Interactive
from interactive.log import set_log_level, info, INFO, critical
from interactive.memory import report_memory_usage_and_free
from interactive.polyfills.animation import ORANGE, BLACK
from interactive.polyfills.pixel import new_pixels

REPORT_RAM = are_pins_available()

BUTTON_PIN = None

BUZZER_PIN = None

AUDIO_PIN = None
AUDIO_FILE = "lion.mp3"

ULTRASONIC_TRIGGER_PIN = None
ULTRASONIC_ECHO_PIN = None

PIXEL_BRIGHTNESS = 1.0
PIXEL_OFF = 0.0
PIXEL_SPEED = 0.1
PIXEL_COLOUR = ORANGE
PIXEL_PINS = []

# Default settings
if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    BUTTON_PIN = board.GP27

    BUZZER_PIN = board.GP2

    AUDIO_PIN = board.GP3

    ULTRASONIC_TRIGGER_PIN = board.GP7
    ULTRASONIC_ECHO_PIN = board.GP6

    PIXEL_PINS = [board.GP10, board.GP11, board.GP12, board.GP13, board.GP14, board.GP15]

if __name__ == '__main__':

    set_log_level(INFO)

    if REPORT_RAM:
        report_memory_usage_and_free("Before creating Objects")

    # Try loading local device settings as overrides.
    try:
        # noinspection PyPackageRequirements
        from config import *

        info("Config file loaded")

    except ImportError:
        info("No config file was found")

    pixels = [new_pixels(pin, 8, brightness=PIXEL_BRIGHTNESS) for pin in PIXEL_PINS if pin is not None]
    animations = [Flicker(pixel, speed=PIXEL_SPEED, color=PIXEL_COLOUR) for pixel in pixels]


    async def cancel() -> None:
        for animation in animations:
            animation.freeze()

        for pixel in pixels:
            pixel.fill(BLACK)
            pixel.write()


    async def start_trigger() -> None:
        interactive.audio_controller.queue(AUDIO_FILE)
        for pixel in pixels:
            pixel.brightness = PIXEL_BRIGHTNESS


    async def run_trigger() -> None:
        for animation in animations:
            animation.animate()
        critical("start_strigger() called")


    async def stop_trigger() -> None:
        for pixel in pixels:
            pixel.brightness = PIXEL_OFF
            pixel.show()
        critical("stop_strigger() called")


    config = get_node_config()
    config.button_pin = BUTTON_PIN
    config.buzzer_pin = BUZZER_PIN
    config.audio_pin = AUDIO_PIN
    config.ultrasonic_trigger_pin = ULTRASONIC_TRIGGER_PIN
    config.ultrasonic_echo_pin = ULTRASONIC_ECHO_PIN
    config.trigger_start = start_trigger
    config.trigger_run = run_trigger
    config.trigger_stop = stop_trigger
    interactive = Interactive(config)

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + 60


    async def callback() -> None:
        interactive.cancel = time.monotonic() > finish
        if interactive.cancel:
            await cancel()


    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    interactive.run(callback)

    if REPORT_RAM:
        report_memory_usage_and_free("After running Runner")
