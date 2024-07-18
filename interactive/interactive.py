import textwrap

from interactive.button import ButtonController
from interactive.buzzer import BuzzerController
from interactive.environment import is_running_on_desktop
from interactive.log import info, INFO, debug
from interactive.polyfills.button import new_button
from interactive.polyfills.buzzer import new_buzzer
from interactive.runner import Runner

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

        def __str__(self):
            return textwrap.dedent(f"""\
            Button: {self.button_pin}
            Buzzer: {self.buzzer_pin}; volume: {self.buzzer_volume}""")

        def log(self, level):
            for s in self.__str__().split('\n'):
                info(s)

    def __init__(self, config: Config):
        self.config = config
        self.runner = Runner()
        self.runner.add_loop_task(self.__cancel_buzzer)

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

    async def __cancel_buzzer(self) -> None:
        if self.runner.cancel and self.buzzer_controller:
            debug('Turning off the buzzer')
            self.buzzer_controller.off()

    async def __single_click_handler(self) -> None:
        if not self.runner.cancel and self.buzzer_controller:
            self.buzzer_controller.beep()

    async def __multi_click_handler(self) -> None:
        if not self.runner.cancel and self.buzzer_controller:
            self.buzzer_controller.beeps(2)

    async def __long_press_handler(self) -> None:
        if not self.runner.cancel and self.buzzer_controller:
            self.buzzer_controller.beeps(5)
