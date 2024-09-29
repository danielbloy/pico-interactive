# NOTE: Rename this to config.py on the primary node path microcontroller.
# This code runs on a Pimoroni Tiny 2040
import board

BUTTON_PIN = board.GP0
AUDIO_PIN = board.GP26

SKULL_PINS = [board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, board.GP6]
PRIMARY_NODE = True

TRIGGER_PIN = board.GP29
TRIGGER_DURATION = 30
REPORT_RAM = True
REPORT_RAM_PERIOD = 10

from interactive.log import CRITICAL

LOG_LEVEL = CRITICAL
