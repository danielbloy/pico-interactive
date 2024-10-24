# NOTE: Rename this to config.py on the primary node network microcontroller.
# This code runs on a standard Pico 2040
import board

BUTTON_PIN = board.GP0

LOCAL_TRIGGER_PIN = board.GP9
REMOTE_TRIGGER_PIN = board.GP1
TRIGGER_DURATION = 40

REPORT_RAM = False
REPORT_RAM_PERIOD = 10

from interactive.log import CRITICAL

LOG_LEVEL = CRITICAL
