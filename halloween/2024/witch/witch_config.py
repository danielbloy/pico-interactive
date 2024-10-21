# NOTE: Rename this to config.py on the witch node.
# This code runs on a standard Pico 2040, using the 2023 box.
import board

AUDIO_PIN = board.GP26

CAULDRON_PIN = board.GP28

TRIGGER_PIN = board.GP9
TRIGGER_DURATION = 40

REPORT_RAM = False
REPORT_RAM_PERIOD = 10

from interactive.log import CRITICAL

LOG_LEVEL = CRITICAL
