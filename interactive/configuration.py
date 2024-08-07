# This file is used to setup the default configuration for a typical node.
# Using it removes some boilerplate from the node code. It also sets up
# the logging level. The values in here are expected can be overridden
# through settings in a config.py file.
from interactive.environment import are_pins_available
from interactive.interactive import Interactive
from interactive.log import set_log_level, INFO
from interactive.memory import report_memory_usage

REPORT_RAM = False
REPORT_RAM_PERIOD = 5  # This is the period in seconds between each report.

GARBAGE_COLLECT = False
GARBAGE_COLLECT_PERIOD = 10  # This is the period in seconds between each forced execution of the garbage collector.

LOG_LEVEL = INFO

BUTTON_PIN = None

BUZZER_PIN = None
BUZZER_VOLUME = 0.1

AUDIO_PIN = None

ULTRASONIC_TRIGGER_PIN = None
ULTRASONIC_ECHO_PIN = None

TRIGGER_DISTANCE = 100
TRIGGER_DURATION = 60

if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    # Default settings
    BUTTON_PIN = board.GP27
    BUZZER_PIN = board.GP2
    AUDIO_PIN = board.GP12
    ULTRASONIC_TRIGGER_PIN = board.GP7
    ULTRASONIC_ECHO_PIN = board.GP6

# Try loading local device settings as overrides.
try:
    # noinspection PyPackageRequirements
    from config import *

    print("Config file loaded")

except ImportError:
    print("No config file was found")

set_log_level(LOG_LEVEL)


def get_node_config(button=True, buzzer=True, audio=True, ultrasonic=True) -> Interactive.Config:
    if REPORT_RAM:
        report_memory_usage("get_node_config")

    config = Interactive.Config()
    if button:
        config.button_pin = BUTTON_PIN

    if buzzer:
        config.buzzer_pin = BUZZER_PIN
        config.buzzer_volume = BUZZER_VOLUME

    if audio:
        config.audio_pin = AUDIO_PIN

    if ultrasonic:
        config.ultrasonic_trigger_pin = ULTRASONIC_TRIGGER_PIN
        config.ultrasonic_echo_pin = ULTRASONIC_ECHO_PIN
        config.trigger_distance = TRIGGER_DISTANCE
        config.trigger_duration = TRIGGER_DURATION

    return config
