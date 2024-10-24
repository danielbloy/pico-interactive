# NOTE: Rename this to config.py on the graveyard node microcontroller.
# This code runs on a Pimoroni Tiny 2040
import board

from interactive.polyfills.animation import RED, ORANGE, AMBER, BLUE, GREEN, YELLOW, WHITE

BUTTON_PIN = board.GP0
AUDIO_PIN = board.GP26

SPIDER_PINS = [board.GP1, board.GP2, board.GP3, board.GP4, board.GP5, board.GP6]
SPIDER_COLOURS = [RED, ORANGE, AMBER, BLUE, GREEN, YELLOW]
SPIDER_PERIODS = [3, 2, 4, 1, 5, 2]

LIGHTNING_PIN = board.GP0
LIGHTNING_COLOUR = WHITE
LIGHTNING_MIN_FLASHES = 5
LIGHTNING_MAX_FLASHES = 15
LIGHTNING_MIN_BRIGHTNESS = 0.1
LIGHTNING_MAX_BRIGHTNESS = 1.0

TRIGGER_PIN = board.GP29
TRIGGER_DURATION = 2
REPORT_RAM = True
REPORT_RAM_PERIOD = 10

from interactive.log import CRITICAL

LOG_LEVEL = CRITICAL
