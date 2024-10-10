from interactive.configuration import Config
from interactive.environment import is_running_on_desktop
from interactive.log import info, debug, critical, CRITICAL
from interactive.memory import setup_memory_reporting
from interactive.runner import Runner

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

        critical('Running with config:')
        config.log(CRITICAL)

        self.runner = Runner()

        self.runner.cancel_on_exception = False
        self.runner.restart_on_exception = True
        self.runner.restart_on_completion = False
        self.runner.add_loop_task(self.__cancel_operations)

        self.server = None
        self.network_controller = None

        if config.network:
            from interactive.network import NetworkController
            from interactive.polyfills.network import new_server
            self.server = new_server()
            self.network_controller = NetworkController(self.server)
            self.network_controller.register(self.runner)

        self.directory_service = None
        if config.directory:
            from interactive.directory import DirectoryService
            self.directory_service = DirectoryService()
            self.network_controller.server.add_routes(self.directory_service.get_routes())
            self.directory_service.register(self.runner)

        self.button = None
        self.button_controller = None

        if config.button_pin:
            from interactive.button import ButtonController
            from interactive.polyfills.button import new_button

            self.button = new_button(config.button_pin)
            self.button_controller = ButtonController(self.button)
            if config.button_single_press:
                self.button_controller.add_single_press_handler(config.button_single_press)
            if config.button_multi_press:
                self.button_controller.add_multi_press_handler(config.button_multi_press)
            if config.button_long_press:
                self.button_controller.add_long_press_handler(config.button_long_press)

            self.button_controller.register(self.runner)

        self.buzzer = None
        self.buzzer_controller = None

        if config.buzzer_pin:
            from interactive.buzzer import BuzzerController
            from interactive.polyfills.buzzer import new_buzzer
            self.buzzer = new_buzzer(config.buzzer_pin)
            self.buzzer.volume = config.buzzer_volume
            self.buzzer_controller = BuzzerController(self.buzzer)
            self.buzzer_controller.register(self.runner)

        self.audio = None
        self.audio_controller = None

        if config.audio_pin:
            from interactive.audio import AudioController
            from interactive.polyfills.audio import new_mp3_player
            # we need a valid tiny file to load otherwise it will error. I got this file from:
            #    https://github.com/mathiasbynens/small
            self.audio = new_mp3_player(config.audio_pin, "interactive/mp3.mp3")
            self.audio_controller = AudioController(self.audio)
            self.audio_controller.register(self.runner)

        self.ultrasonic = None
        self.ultrasonic_controller = None

        if config.ultrasonic_trigger_pin is not None and config.ultrasonic_echo_pin is not None:
            from interactive.polyfills.ultrasonic import new_ultrasonic
            from interactive.ultrasonic import UltrasonicController
            self.ultrasonic = new_ultrasonic(config.ultrasonic_trigger_pin, config.ultrasonic_echo_pin)
            self.ultrasonic_controller = UltrasonicController(self.ultrasonic)
            self.ultrasonic_controller.register(self.runner)
            self.ultrasonic_controller.add_trigger(
                config.trigger_distance, self.__trigger_handler, config.trigger_duration)

        self.triggerable = None
        if self.ultrasonic_controller is not None or config.trigger_duration is not None:
            from interactive.scheduler import new_triggered_task, Triggerable

            self.triggerable = Triggerable()

            trigger_loop = new_triggered_task(
                self.triggerable,
                duration=config.trigger_duration,
                start=config.trigger_start,
                run=config.trigger_run,
                stop=config.trigger_stop)
            self.runner.add_task(trigger_loop)

        setup_memory_reporting(self.runner)

    @property
    def cancel(self) -> bool:
        return self.runner.cancel

    @cancel.setter
    def cancel(self, cancel: bool) -> None:
        self.runner.cancel = cancel

    def run(self, callback: Callable[[], Awaitable[None]] = None) -> None:
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

    async def __trigger_handler(self, distance: float, actual: float) -> None:
        info(f"Distance {distance} handler triggered: {actual}")
        self.triggerable.triggered = True
