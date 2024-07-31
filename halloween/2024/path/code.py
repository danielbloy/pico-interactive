# Entry point for a path node. This supports both path nodes that are on either
# side of the path. One will be the primary node and the other the secondary.

from interactive.environment import are_pins_available
from interactive.interactive import Interactive
from interactive.log import set_log_level, info, INFO

BUTTON_PIN = None

BUZZER_PIN = None
BUZZER_VOLUME = 0.1

ULTRASONIC_TRIGGER_PIN = None
ULTRASONIC_ECHO_PIN = None

TRIGGER_DISTANCE = 100
TRIGGER_DURATION = 60

# Default settings
if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    BUTTON_PIN = board.GP27

    BUZZER_PIN = board.GP2

    ULTRASONIC_TRIGGER_PIN = board.GP7
    ULTRASONIC_ECHO_PIN = board.GP6

    SKULL_PINS = [board.GP10, board.GP11, board.GP12, board.GP13, board.GP14, board.GP15]

if __name__ == '__main__':

    set_log_level(INFO)

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
    config.trigger_start = start_display
    config.trigger_run = run_display
    config.trigger_stop = stop_display

    interactive = Interactive(config)


    async def callback() -> None:
        if interactive.cancel:
            await cancel()


    interactive.run(callback)
