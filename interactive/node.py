# This function is used to setup the default configuration for a typical node.
# Using it removes some boilerplate from the node code.
from interactive.environment import are_pins_available
from interactive.interactive import Interactive
from interactive.log import info

BUTTON_PIN = None

BUZZER_PIN = None
BUZZER_VOLUME = 0.1

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
    ULTRASONIC_TRIGGER_PIN = board.GP7
    ULTRASONIC_ECHO_PIN = board.GP6


def get_node_config() -> Interactive.Config:
    # Try loading local device settings as overrides.
    try:
        # noinspection PyPackageRequirements
        from config import *

        info("Config file loaded")

    except ImportError:
        info("No config file was found")

    config = Interactive.Config()
    config.buzzer_pin = BUZZER_PIN
    config.button_pin = BUTTON_PIN
    config.buzzer_volume = BUZZER_VOLUME
    config.ultrasonic_trigger_pin = ULTRASONIC_TRIGGER_PIN
    config.ultrasonic_echo_pin = ULTRASONIC_ECHO_PIN
    config.trigger_distance = TRIGGER_DISTANCE
    config.trigger_duration = TRIGGER_DURATION

    return config
