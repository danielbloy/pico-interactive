# NOTE: Rename this to code.py on the secondary node path microcontroller.
# This code runs on a standard Pico 2040
import board

from path import run_path

SKULL_PIXELS_PINS = [board.GP5, board.GP6, board.GP7, board.GP8, board.GP9, board.GP10]

run_path(SKULL_PIXELS_PINS)
