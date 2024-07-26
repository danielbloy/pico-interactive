import time

from interactive.button import ButtonController
from interactive.environment import are_pins_available
from interactive.log import set_log_level, INFO, info
from interactive.polyfills.button import new_button
from interactive.polyfills.ultrasonic import new_ultrasonic
from interactive.runner import Runner
from interactive.ultrasonic import UltrasonicTrigger

BUTTON_PIN = None
ULTRASONIC_TRIGGER_PIN = None
ULTRASONIC_ECHO_PIN = None

if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    BUTTON_PIN = board.GP27
    ULTRASONIC_TRIGGER_PIN = board.GP27
    ULTRASONIC_ECHO_PIN = board.GP27

if __name__ == '__main__':
    set_log_level(INFO)

    runner = Runner()

    ultrasonic = new_ultrasonic(ULTRASONIC_TRIGGER_PIN, ULTRASONIC_ECHO_PIN)

    trigger = UltrasonicTrigger(ultrasonic)
    # TODO: Register distance events.
    trigger.register(runner)


    async def single_click_handler() -> None:
        info(f"Distance: {ultrasonic.distance}")


    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_click_handler(single_click_handler)
    button_controller.register(runner)

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + 10


    async def callback() -> None:
        runner.cancel = time.monotonic() > finish


    runner.run(callback)
