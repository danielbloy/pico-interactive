# Entry point for a path node. This supports both path nodes that are on either
# side of the path. One will be the primary node and the other the secondary.
import asyncio

import board

from interactive.animation import Flicker
from interactive.interactive import Interactive
from interactive.log import info
from interactive.polyfills.animation import ORANGE, BLACK
from interactive.polyfills.pixel import new_pixels

SKULL_BRIGHTNESS = 1.0
SKULL_OFF = 0.0
SKULL_SPEED = 0.1
SKULL_COLOUR = ORANGE
SKULL_PINS = [board.GP10, board.GP11, board.GP12, board.GP13, board.GP14, board.GP15]

# Perform import of configuration here to allow for overrides from the config file.
from interactive.configuration import *

pixels = [new_pixels(pin, 8, brightness=SKULL_BRIGHTNESS) for pin in SKULL_PINS if pin is not None]
animations = [Flicker(pixel, speed=SKULL_SPEED, color=SKULL_COLOUR) for pixel in pixels]


async def cancel() -> None:
    # TODO: This could probably just call stop_display()
    for animation in animations:
        animation.freeze()

    for pixel in pixels:
        pixel.fill(BLACK)
        pixel.write()


async def start_display() -> None:
    interactive.audio_controller.queue("lion.mp3")
    for pixel in pixels:
        pixel.brightness = SKULL_BRIGHTNESS

    t1 = asyncio.create_task(test_task_1())
    t2 = asyncio.create_task(test_task_2())


async def run_display() -> None:
    for animation in animations:
        animation.animate()


async def stop_display() -> None:
    for pixel in pixels:
        pixel.brightness = SKULL_OFF
        pixel.show()


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


config = get_node_config(button=False, buzzer=False, ultrasonic=False)
config.trigger_start = start_display()
config.trigger_run = run_display()
config.trigger_stop = stop_display()

interactive = Interactive(config)


async def callback() -> None:
    if interactive.cancel:
        await cancel()


interactive.run(callback)
