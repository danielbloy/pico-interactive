# Entry point for a path node. This supports both path nodes that are on either
# side of the path. One will be the primary node and the other the secondary.

# TODO: This is boilerplate and should be moved into common code.

from interactive.environment import are_pins_available
from interactive.interactive import Interactive
from interactive.log import set_log_level, info, INFO

PRIMARY = True
BUTTON_PIN = None
BUZZER_PIN = None
BUZZER_VOLUME = 0.1

# Default settings
if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    BUTTON_PIN = board.GP27
    BUZZER_PIN = board.GP2

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

    interactive = Interactive(config)


    async def callback() -> None:
        pass


    interactive.run(callback)
