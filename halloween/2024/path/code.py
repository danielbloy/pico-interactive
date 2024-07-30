# Entry point for a path node. This supports both path nodes that are on either
# side of the path. One will be the primary node and the other the secondary.
import asyncio
import time

from interactive.animation import Flicker
from interactive.environment import are_pins_available
from interactive.interactive import Interactive
from interactive.log import set_log_level, info, INFO
from interactive.polyfills.animation import ORANGE, BLACK
from interactive.polyfills.pixel import new_pixels

PRIMARY = True

BUTTON_PIN = None

BUZZER_PIN = None
BUZZER_VOLUME = 0.1

ULTRASONIC_TRIGGER_PIN = None
ULTRASONIC_ECHO_PIN = None

TRIGGER_DISTANCE = 100
TRIGGER_DURATION = 60

SKULL_BRIGHTNESS = 1.0
SKULL_OFF = 0.0
SKULL_SPEED = 0.1
SKULL_COLOUR = ORANGE
SKULL_PINS = [None, None, None, None, None, None]

# Default settings
if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    BUTTON_PIN = board.GP27

    BUZZER_PIN = board.GP2

    ULTRASONIC_TRIGGER_PIN = board.GP7
    ULTRASONIC_ECHO_PIN = board.GP6

    SKULL_PINS = [board.GP10, board.GP11, board.GP12, board.GP13, board.GP14, board.GP15]

pixels = [new_pixels(pin, 8, brightness=SKULL_BRIGHTNESS) for pin in SKULL_PINS if pin is not None]
animations = [Flicker(pixel, speed=SKULL_SPEED, color=SKULL_COLOUR) for pixel in pixels]


async def stop_display() -> None:
    for pixel in pixels:
        pixel.brightness = SKULL_OFF
        pixel.show()


async def start_display() -> None:
    for pixel in pixels:
        pixel.brightness = SKULL_BRIGHTNESS

    t1 = asyncio.create_task(test_task_1())
    t2 = asyncio.create_task(test_task_2())


async def run_display() -> None:
    for animation in animations:
        animation.animate()


async def test_task_1() -> None:
    info("Start test task 1")
    await asyncio.sleep(2)
    for pixel in pixels:
        pixel.brightness = SKULL_OFF
        pixel.show()
    info("End test task 1")


async def test_task_2() -> None:
    info("Start test task 2")
    await asyncio.sleep(1)
    info("End test task 2")


if __name__ == '__main__':

    set_log_level(INFO)

    # Try loading local device settings as overrides.
    try:
        # noinspection PyPackageRequirements
        from config import *

        info("Config file loaded")

    except ImportError:
        info("No config file was found")

    config = Interactive.Config()
    config.buzzer_pin = BUZZER_PIN
    config.button_pin = BUTTON_PIN
    config.buzzer_volume = BUZZER_VOLUME
    config.ultrasonic_trigger_pin = ULTRASONIC_TRIGGER_PIN
    config.ultrasonic_echo_pin = ULTRASONIC_ECHO_PIN

    triggered = False
    running = False
    stop_time = 0


    async def trigger_handler(distance: float, actual: float) -> None:
        info(f"Distance {distance} handler triggered: {actual}")
        global triggered
        triggered = True


    async def trigger_events() -> None:
        global triggered, running, stop_time

        # Check for stop display
        if running and time.time() >= stop_time:
            info("Stop running trigger event")
            running = False
            await stop_display()

        # Check for start display
        if triggered and not running:
            info("Start running trigger event")
            stop_time = time.time() + TRIGGER_DURATION
            running = True
            await start_display()

        triggered = False

        if running:
            await run_display()


    interactive = Interactive(config)
    interactive.trigger.add_trigger(TRIGGER_DISTANCE, trigger_handler, TRIGGER_DURATION)
    interactive.runner.add_loop_task(trigger_events)


    async def callback() -> None:
        if interactive.cancel:
            for animation in animations:
                animation.freeze()

            for pixel in pixels:
                pixel.fill(BLACK)
                pixel.write()


    interactive.run(callback)
