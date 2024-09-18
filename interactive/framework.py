import gc

from interactive.configuration import Config
from interactive.environment import is_running_on_desktop
from interactive.log import critical, info, debug, CRITICAL
from interactive.memory import report_memory_usage, report_memory_usage_and_free
from interactive.runner import Runner
from interactive.scheduler import new_triggered_task, Triggerable, TriggerableAlwaysOn, terminate_on_cancel

if is_running_on_desktop():
    from collections.abc import Callable, Awaitable


class Interactive:
    """
    Interactive is the entry point class and sets up a running environment based on the
    configuration provided by a Config instance. Interactive will create all the
    necessary instances to control the buzzer, button etc. Most of the configuration
    properties are optional and will only invoke the relevant control objects if
    valid properties are provided. Interactive also sets up the runner to be more
    tolerant of failures by enforcing the following runner properties:
      * cancel_on_exception = False
      * restart_on_exception = True
    """

    def __init__(self, config: Config):

        if config.report_ram:
            report_memory_usage("Interactive.__init__() start")

        self.config = config
        self.runner = Runner()

        self.runner.cancel_on_exception = False
        self.runner.restart_on_exception = True
        self.runner.restart_on_completion = False  # TODO: determine if this also needs enabling.
        self.runner.add_loop_task(self.__cancel_operations)

        self.server = None
        self.network_controller = None

        if self.config.network:
            from interactive.network import NetworkController
            from interactive.polyfills.network import new_server
            self.server = new_server()
            self.network_controller = NetworkController(self.server)
            self.network_controller.register(self.runner)

        self.button = None
        self.button_controller = None

        if self.config.button_pin:
            from interactive.button import ButtonController
            from interactive.polyfills.button import new_button

            self.button = new_button(self.config.button_pin)
            self.button_controller = ButtonController(self.button)
            # Allow overrides of the button presses instead of default behaviour.
            if self.config.button_single_press or self.config.button_multi_press or self.config.button_long_press:
                self.button_controller.add_single_click_handler(self.config.button_single_press)
                self.button_controller.add_multi_click_handler(self.config.button_multi_press)
                self.button_controller.add_long_press_handler(self.config.button_long_press)
            else:
                self.button_controller.add_single_click_handler(self.__single_click_handler)
                self.button_controller.add_multi_click_handler(self.__multi_click_handler)
                self.button_controller.add_long_press_handler(self.__long_press_handler)

            self.button_controller.register(self.runner)

        self.buzzer = None
        self.buzzer_controller = None

        if self.config.buzzer_pin:
            from interactive.buzzer import BuzzerController
            from interactive.polyfills.buzzer import new_buzzer
            self.buzzer = new_buzzer(self.config.buzzer_pin)
            self.buzzer.volume = self.config.buzzer_volume
            self.buzzer_controller = BuzzerController(self.buzzer)
            self.buzzer_controller.register(self.runner)

        self.audio = None
        self.audio_controller = None

        if self.config.audio_pin:
            from interactive.audio import AudioController
            from interactive.polyfills.audio import new_mp3_player
            # we need a valid tiny file to load otherwise it will error. I got this file from:
            #    https://github.com/mathiasbynens/small
            self.audio = new_mp3_player(self.config.audio_pin, "interactive/mp3.mp3")
            self.audio_controller = AudioController(self.audio)
            self.audio_controller.register(self.runner)

        self.ultrasonic = None
        self.ultrasonic_controller = None
        self.triggerable = Triggerable()

        if self.config.ultrasonic_trigger_pin is not None and self.config.ultrasonic_echo_pin is not None:
            from interactive.polyfills.ultrasonic import new_ultrasonic
            from interactive.ultrasonic import UltrasonicController
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

        if self.config.report_ram:
            async def report_memory() -> None:
                report_memory_usage("Interactive.report_memory()")

            triggerable = TriggerableAlwaysOn()
            report_memory_task = (
                new_triggered_task(
                    triggerable, self.config.report_ram_period, start=report_memory,
                    cancel_func=terminate_on_cancel(self)))
            self.runner.add_task(report_memory_task)

        if self.config.garbage_collect:
            async def garbage_collect() -> None:
                report_memory_usage_and_free("Interactive.garbage_collect()")

            triggerable = TriggerableAlwaysOn()
            garbage_collect_task = (
                new_triggered_task(
                    triggerable, self.config.garbage_collect_period, stop=garbage_collect,
                    cancel_func=terminate_on_cancel(self)))
            self.runner.add_task(garbage_collect_task)

        gc.collect()

        if self.config.report_ram:
            report_memory_usage("Interactive.__init__() start")

    @property
    def cancel(self) -> bool:
        return self.runner.cancel

    @cancel.setter
    def cancel(self, cancel: bool) -> None:
        self.runner.cancel = cancel

    def run(self, callback: Callable[[], Awaitable[None]] = None) -> None:
        critical('Running with config:')
        self.config.log(CRITICAL)
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
