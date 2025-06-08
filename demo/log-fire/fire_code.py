# NOTE: Rename this to code.py on each log-fire microcontroller.

import board

from interactive.animation import Flicker
from interactive.log import CRITICAL
from interactive.memory import setup_memory_reporting
from interactive.polyfills.animation import ORANGE, RED
from interactive.polyfills.pixel import new_pixels
from interactive.runner import Runner

FIRE_PIN_1 = board.GP29
FIRE_PIN_2 = board.GP27
FIRE_COLOUR_PRIMARY = ORANGE
FIRE_COLOUR_SECONDARY = RED
FIRE_BRIGHTNESS = 1.0
FIRE_SPEED = 0.05

LOG_LEVEL = CRITICAL
runner = Runner()

runner.cancel_on_exception = False
runner.restart_on_exception = True
runner.restart_on_completion = True

pixels_1 = new_pixels(FIRE_PIN_1, 100, brightness=FIRE_BRIGHTNESS)
pixels_2 = new_pixels(FIRE_PIN_2, 100, brightness=FIRE_BRIGHTNESS)

animation_1 = Flicker(pixels_1, speed=FIRE_SPEED, color=FIRE_COLOUR_PRIMARY)
animation_2 = Flicker(pixels_2, speed=FIRE_SPEED, color=FIRE_COLOUR_PRIMARY)

for i in range(0, 59, 2):
    animation_1.set(i, FIRE_COLOUR_SECONDARY)
    animation_2.set(i, FIRE_COLOUR_SECONDARY)


# pixels.show()


async def animate_pixels() -> None:
    if not runner.cancel:
        animation_1.animate()
        animation_2.animate()


runner.add_loop_task(animate_pixels)

setup_memory_reporting(runner)
runner.run()
