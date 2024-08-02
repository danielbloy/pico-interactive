import time

from interactive.button import ButtonController
from interactive.environment import are_pins_available
from interactive.log import set_log_level, INFO, info
from interactive.polyfills.button import new_button
from interactive.polyfills.ultrasonic import new_ultrasonic
from interactive.runner import Runner
from interactive.ultrasonic import UltrasonicController

BUTTON_PIN = None
ULTRASONIC_TRIGGER_PIN = None
ULTRASONIC_ECHO_PIN = None

if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    BUTTON_PIN = board.GP27
    ULTRASONIC_TRIGGER_PIN = board.GP7
    ULTRASONIC_ECHO_PIN = board.GP6

if __name__ == '__main__':
    set_log_level(INFO)

    runner = Runner()

    ultrasonic = new_ultrasonic(ULTRASONIC_TRIGGER_PIN, ULTRASONIC_ECHO_PIN)


    async def trigger_handler(distance: float, actual: float) -> None:
        info(f"Distance {distance} handler triggered: {actual}")


    controller = UltrasonicController(ultrasonic)
    controller.add_trigger(100, trigger_handler, 5)
    controller.register(runner)


    async def single_click_handler() -> None:
        info(f"Distance: {ultrasonic.distance}")


    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_click_handler(single_click_handler)
    button_controller.register(runner)

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + 60


    async def callback() -> None:
        runner.cancel = time.monotonic() > finish


    runner.run(callback)
