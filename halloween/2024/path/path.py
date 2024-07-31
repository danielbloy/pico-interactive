import asyncio

from interactive.animation import Flicker
from interactive.environment import are_pins_available
from interactive.log import info
from interactive.polyfills.animation import ORANGE, BLACK
from interactive.polyfills.pixel import new_pixels

SKULL_BRIGHTNESS = 1.0
SKULL_OFF = 0.0
SKULL_SPEED = 0.1
SKULL_COLOUR = ORANGE
SKULL_PINS = [None, None, None, None, None, None]

if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    SKULL_PINS = [board.GP10, board.GP11, board.GP12, board.GP13, board.GP14, board.GP15]

pixels = [new_pixels(pin, 8, brightness=SKULL_BRIGHTNESS) for pin in SKULL_PINS if pin is not None]
animations = [Flicker(pixel, speed=SKULL_SPEED, color=SKULL_COLOUR) for pixel in pixels]


async def cancel() -> None:
    # TODO: This could probable just call stop_display()
    for animation in animations:
        animation.freeze()

    for pixel in pixels:
        pixel.fill(BLACK)
        pixel.write()


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
