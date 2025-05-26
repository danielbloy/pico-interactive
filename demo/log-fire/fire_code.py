# NOTE: Rename this to code.py on each log-fire microcontroller.

import board

from interactive.animation import Flicker
from interactive.log import CRITICAL
from interactive.memory import setup_memory_reporting
from interactive.polyfills.animation import BLACK
from interactive.polyfills.animation import ORANGE
from interactive.polyfills.pixel import new_pixels
from interactive.runner import Runner

AUDIO_PIN = board.GP26

FIRE_PIN = board.GP28
FIRE_COLOUR = ORANGE
FIRE_BRIGHTNESS = 1.0
FIRE_SPEED = 0.1

TRIGGER_PIN = board.GP9
TRIGGER_DURATION = 40

REPORT_RAM = False
REPORT_RAM_PERIOD = 10

LOG_LEVEL = CRITICAL

runner = Runner()

runner.cancel_on_exception = False
runner.restart_on_exception = True
runner.restart_on_completion = True

pixels = new_pixels(FIRE_PIN, 60, brightness=FIRE_BRIGHTNESS)
animation = Flicker(pixels, speed=FIRE_SPEED, color=FIRE_COLOUR)

pixels.fill(FIRE_COLOUR)
pixels.brightness = FIRE_BRIGHTNESS
pixels.show()


async def animate_pixels() -> None:
    if not runner.cancel:
        if animation:
            animation.animate()


runner.add_loop_task(animate_pixels)

setup_memory_reporting(runner)
runner.run()

pixels.fill(BLACK)
pixels.brightness = 0
pixels.show()
