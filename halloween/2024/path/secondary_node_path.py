# NOTE: Rename this to code.py on the secondary node path microcontroller.
# This code runs on a standard Pico 2040

import board

from interactive.configuration import get_node_config
from interactive.framework import Interactive
from path import PathController

SKULL_PIXELS_PINS = [board.GP5, board.GP6, board.GP7, board.GP8, board.GP9, board.GP10]


async def cancel() -> None:
    await pathController.stop_display()


async def trigger_display() -> None:
    interactive.triggerable.triggered = True


async def start_display() -> None:
    await pathController.start_display()


async def run_display() -> None:
    await pathController.run_display()


async def stop_display() -> None:
    await pathController.stop_display()


# TODO: The ultrasonic sensor is used to trigger the display; even though we may not actually use it.
config = get_node_config(network=False, button=True, buzzer=False, audio=True, ultrasonic=True)
config.trigger_start = start_display
config.trigger_run = run_display
config.trigger_stop = stop_display

config.button_single_press = trigger_display


async def callback() -> None:
    if interactive.cancel:
        await cancel()


interactive = Interactive(config)

pathController = PathController(SKULL_PIXELS_PINS, interactive.audio_controller)

interactive.run(callback)
