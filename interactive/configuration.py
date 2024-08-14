# This file is used to setup the default configuration for a typical node.
# Using it removes some boilerplate from the node code. It also sets up
# the logging level. The values in here are expected can be overridden
# through settings in a config.py file.
from interactive.environment import are_pins_available
from interactive.log import set_log_level, INFO, log
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
    AUDIO_PIN = board.GP26
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


class Config:
    """
    Holds the configuration settings required for constructing an instance of
    Interactive.
    """

    def __init__(self):
        self.report_ram = False
        self.report_ram_period = 9999
        self.garbage_collect = False
        self.garbage_collect_period = 9999
        self.network = False
        self.button_pin = None
        self.buzzer_pin = None
        self.buzzer_volume = 1.0
        self.audio_pin = None
        self.ultrasonic_trigger_pin = None
        self.ultrasonic_echo_pin = None
        self.trigger_distance = 9999
        self.trigger_duration = 0
        self.trigger_start = None
        self.trigger_run = None
        self.trigger_stop = None

    def __str__(self):
        return f"""
          Ram:
            Report ............ : {self.report_ram}
            Period ............ : {self.report_ram_period} seconds
          Garbage Collection:
            Force ............. : {self.garbage_collect}
            Period ............ : {self.garbage_collect_period} seconds
          Network:
            Enabled ........... : {self.network}
          Button: 
            Pin ............... : {self.button_pin}
          Buzzer: 
            Pin ............... : {self.buzzer_pin}
            Volume ............ : {self.buzzer_volume}
          Audio:
            Pin ............... : {self.audio_pin}
          Ultrasonic Sensor:
            Trigger ........... : {self.ultrasonic_trigger_pin}
            Echo .............. : {self.ultrasonic_echo_pin}
          Trigger:
            Distance .......... : {self.trigger_distance} cm
            Duration .......... : {self.trigger_duration} seconds
          """

    def log(self, level):
        for s in self.__str__().split('\n'):
            log(level, s)


def get_node_config(network=False, button=True, buzzer=True, audio=True, ultrasonic=True) -> Config:
    if REPORT_RAM:
        report_memory_usage("get_node_config")

    config = Config()

    config.network = network

    if REPORT_RAM:
        config.report_ram = True
        config.report_ram_period = REPORT_RAM_PERIOD

    if GARBAGE_COLLECT:
        config.garbage_collect = True
        config.garbage_collect_period = GARBAGE_COLLECT_PERIOD

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
