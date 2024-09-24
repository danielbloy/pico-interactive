# NOTE: Rename this to code.py on the secondary node path microcontroller.
# This code runs on a standard Pico 2040
import board

BUTTON_PIN = board.GP26
AUDIO_PIN = board.GP22
ULTRASONIC_TRIGGER_PIN = board.GP17
ULTRASONIC_ECHO_PIN = board.GP16

SKULL_PINS = [board.GP5, board.GP6, board.GP7, board.GP8, board.GP9, board.GP10]
PRIMARY_NODE = False

TRIGGER_DURATION = 10
REPORT_RAM = True
REPORT_RAM_PERIOD = 10

from interactive.log import CRITICAL

LOG_LEVEL = CRITICAL
