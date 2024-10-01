# NOTE: Rename this to config.py on the ultrasonic node microcontroller.
# This code runs on a standard Pico 2040
import board

NODE_COORDINATOR = "192.168.1.248:5001"

BUTTON_PIN = board.GP26

ULTRASONIC_TRIGGER_PIN = board.GP17
ULTRASONIC_ECHO_PIN = board.GP16
TRIGGER_DISTANCE = 100
TRIGGER_DURATION = 30

REPORT_RAM = True
REPORT_RAM_PERIOD = 10

from interactive.log import CRITICAL

LOG_LEVEL = CRITICAL
