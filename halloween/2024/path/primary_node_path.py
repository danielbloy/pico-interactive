# NOTE: Rename this to code.py on the primary node path microcontroller.
# This code runs on a Pimoroni Tiny 2040
import board

from path import run_path

SKULL_PIXELS_PINS = [board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, board.GP6]

run_path(SKULL_PIXELS_PINS)
