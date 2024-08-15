# Tests running the following pico interactive components together
# on a single microcontroller to check RAM and space limits:
#  * Runner
#  * Button
#  * Ultrasonic
#  * Network
#
import time

from interactive.button import ButtonController
from interactive.environment import are_pins_available
from interactive.log import set_log_level, INFO, critical
from interactive.memory import report_memory_usage_and_free
from interactive.network import NetworkController
from interactive.polyfills.button import new_button
from interactive.polyfills.network import new_server
from interactive.polyfills.ultrasonic import new_ultrasonic
from interactive.runner import Runner
from interactive.ultrasonic import UltrasonicController

REPORT_RAM = are_pins_available()
REPORT_RAM_PERIODIC = REPORT_RAM and True
REPORT_RAM_PERIOD = 5

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

    if REPORT_RAM:
        report_memory_usage_and_free("Before creating Objects")


    async def single_click_handler() -> None:
        critical('Single click!')
        # TODO: Send network message


    runner = Runner()

    if REPORT_RAM_PERIODIC:
        async def report_memory() -> None:
            from interactive.memory import report_memory_usage
            report_memory_usage("Periodic report RAM")


        from interactive.scheduler import TriggerableAlwaysOn, new_triggered_task, terminate_on_cancel

        triggerable = TriggerableAlwaysOn()
        report_memory_task = (
            new_triggered_task(
                triggerable, REPORT_RAM_PERIOD, start=report_memory,
                cancel_func=terminate_on_cancel(runner)))
        runner.add_task(report_memory_task)

    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_click_handler(single_click_handler)
    button_controller.register(runner)

    ultrasonic = new_ultrasonic(ULTRASONIC_TRIGGER_PIN, ULTRASONIC_ECHO_PIN)


    async def trigger_handler(distance: float, actual: float) -> None:
        critical(f"Distance {distance} handler triggered: {actual}")
        # TODO: Send network message


    controller = UltrasonicController(ultrasonic)
    controller.add_trigger(100, trigger_handler, 5)
    controller.register(runner)

    server = new_server()
    network_controller = NetworkController(server)
    network_controller.register(runner)

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + 10


    async def callback() -> None:
        runner.cancel = time.monotonic() > finish


    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    runner.run(callback)

    if REPORT_RAM:
        report_memory_usage_and_free("After running Runner")
