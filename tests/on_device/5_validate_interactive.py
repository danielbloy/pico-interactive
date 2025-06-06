import time

from interactive.configuration import Config
from interactive.environment import are_pins_available, is_running_on_microcontroller
from interactive.framework import Interactive
from interactive.log import set_log_level, info, INFO
from interactive.memory import report_memory_usage_and_free

REPORT_RAM = is_running_on_microcontroller()

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

    if REPORT_RAM:
        report_memory_usage_and_free("Before creating Objects")

    # Try loading local device settings as overrides.
    try:
        # noinspection PyPackageRequirements
        from config import *

        info("Config file loaded")

    except ImportError:
        info("No config file was found")

    config = Config()
    config.buzzer_pin = BUZZER_PIN
    config.button_pin = BUTTON_PIN
    config.buzzer_volume = BUZZER_VOLUME

    interactive = Interactive(config)

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + 10


    async def callback() -> None:
        interactive.cancel = time.monotonic() > finish


    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    interactive.run(callback)

    if REPORT_RAM:
        report_memory_usage_and_free("After running Runner")
