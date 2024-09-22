# NOTE: Rename this to code.py on the primary node path microcontroller.
# This code runs on a Pimoroni Tiny 2040
import board

from interactive.configuration import get_node_config
from interactive.framework import Interactive
from path import PathController

SKULL_PIXELS_PINS = [board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, board.GP6]


async def cancel() -> None:
    pass


async def start_display() -> None:
    await pathController.start_display()


async def run_display() -> None:
    await pathController.run_display()


async def stop_display() -> None:
    await pathController.stop_display()


config = get_node_config(network=False, button=True, buzzer=False, audio=True, ultrasonic=True)
config.trigger_start = start_display
config.trigger_run = run_display
config.trigger_stop = stop_display

config.button_single_press = start_display


async def callback() -> None:
    if interactive.cancel:
        await cancel()


interactive = Interactive(config)

pathController = PathController(SKULL_PIXELS_PINS, interactive.audio_controller)

interactive.run(callback)
