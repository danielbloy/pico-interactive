import gc

from interactive.audio import AudioController
from interactive.button import ButtonController
from interactive.buzzer import BuzzerController
from interactive.configuration import REPORT_RAM
from interactive.environment import is_running_on_desktop
from interactive.log import info, INFO, debug, log
from interactive.memory import report_memory_usage
from interactive.polyfills.audio import new_mp3_player
from interactive.polyfills.button import new_button
from interactive.polyfills.buzzer import new_buzzer
from interactive.polyfills.ultrasonic import new_ultrasonic
from interactive.runner import Runner
from interactive.scheduler import new_triggered_task, Triggerable
from interactive.ultrasonic import UltrasonicController

if is_running_on_desktop():
    from collections.abc import Callable, Awaitable


class Interactive:
    """
    Interactive is the entry point class and sets up a running environment based on the
    configuration provided bby a Config instance. Interactive will create all the
    necessary instances to control the buzzer, button etc. Most of the configuration
    properties are optional and will only invoke the relevant control objects if
    valid properties are provided. This allows a large range of boards to be supported.
    """

    class Config:
        """
        Holds the configuration settings required for constructing an instance of
        Interactive.
        """

        def __init__(self):
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

    def __init__(self, config: Config):
        if REPORT_RAM:
            report_memory_usage("Interactive.__init__() start")

        self.config = config
        self.runner = Runner()
        self.runner.add_loop_task(self.__cancel_operations)

        self.button = None
        self.button_controller = None

        if self.config.button_pin:
            self.button = new_button(self.config.button_pin)
            self.button_controller = ButtonController(self.button)
            self.button_controller.add_single_click_handler(self.__single_click_handler)
            self.button_controller.add_multi_click_handler(self.__multi_click_handler)
            self.button_controller.add_long_press_handler(self.__long_press_handler)
            self.button_controller.register(self.runner)

        self.buzzer = None
        self.buzzer_controller = None

        if self.config.buzzer_pin:
            self.buzzer = new_buzzer(self.config.buzzer_pin)
            self.buzzer.volume = self.config.buzzer_volume
            self.buzzer_controller = BuzzerController(self.buzzer)
            self.buzzer_controller.register(self.runner)

        self.audio = None
        self.audio_controller = None

        if self.config.audio_pin:
            # we need a valid tiny file to load otherwise it will error. I got this file from:
            #    https://github.com/mathiasbynens/small
            self.audio = new_mp3_player(self.config.audio_pin, "interactive/mp3.mp3")
            self.audio_controller = AudioController(self.audio)
            self.audio_controller.register(self.runner)

        self.ultrasonic = None
        self.ultrasonic_controller = None
        self.triggerable = Triggerable()

        if self.config.ultrasonic_trigger_pin is not None and self.config.ultrasonic_echo_pin is not None:
            self.ultrasonic = new_ultrasonic(self.config.ultrasonic_trigger_pin, self.config.ultrasonic_echo_pin)
            self.ultrasonic_controller = UltrasonicController(self.ultrasonic)
            self.ultrasonic_controller.register(self.runner)
            self.ultrasonic_controller.add_trigger(
                self.config.trigger_distance, self.__trigger_handler, self.config.trigger_duration)

            trigger_loop = new_triggered_task(
                self.triggerable,
                duration=self.config.trigger_duration,
                start=self.config.trigger_start,
                run=self.config.trigger_run,
                stop=self.config.trigger_stop)
            self.runner.add_loop_task(trigger_loop)

        gc.collect()

        if REPORT_RAM:
            report_memory_usage("Interactive.__init__() finish")

    @property
    def cancel(self) -> bool:
        return self.runner.cancel

    @cancel.setter
    def cancel(self, cancel: bool) -> None:
        self.runner.cancel = cancel

    def run(self, callback: Callable[[], Awaitable[None]] = None) -> None:
        info('Running with config:')
        self.config.log(INFO)
        self.runner.run(callback)

    async def __cancel_operations(self) -> None:
        """
        Ensures everything is turned off when the system is ready to terminate.
        """
        if self.runner.cancel:
            if self.buzzer_controller:
                debug('Turning off the buzzer')
                self.buzzer_controller.off()

            if self.audio_controller:
                debug('Turning off the audio')
                self.audio_controller.cancel()

    async def __single_click_handler(self) -> None:
        if not self.runner.cancel and self.buzzer_controller:
            # TODO: This needs to be a proper action
            self.buzzer_controller.beep()

    async def __multi_click_handler(self) -> None:
        if not self.runner.cancel and self.buzzer_controller:
            # TODO: This needs to be a proper action
            self.buzzer_controller.beeps(2)

    async def __long_press_handler(self) -> None:
        if not self.runner.cancel and self.buzzer_controller:
            # TODO: This needs to be a proper action
            self.buzzer_controller.beeps(5)

    async def __trigger_handler(self, distance: float, actual: float) -> None:
        info(f"Distance {distance} handler triggered: {actual}")
        self.triggerable.triggered = True
