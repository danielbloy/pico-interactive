import time

from interactive.environment import are_pins_available, is_running_on_microcontroller
from interactive.log import set_log_level, INFO, info
from interactive.memory import report_memory_usage_and_free
from interactive.microphone import MicrophoneController
from interactive.polyfills.microphone import Microphone
from interactive.runner import Runner

REPORT_RAM = is_running_on_microcontroller()

MICROPHONE_PIN = None

if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    MICROPHONE_PIN = board.A0

if __name__ == '__main__':

    set_log_level(INFO)

    if REPORT_RAM:
        report_memory_usage_and_free("Before creating Objects")

    runner = Runner()

    microphone = Microphone(MICROPHONE_PIN)
    microphone_controller = MicrophoneController(microphone, frequency=120)
    microphone_controller.register(runner)

    report_type = 0
    divisor = microphone.max / 100


    async def handle_sample(minimum, maximum: int) -> None:

        if report_type == 0:
            # Just report amplitude
            amplitude = maximum - minimum
            percent = int(amplitude / divisor)
            info(f"{minimum:6} {maximum:6} {percent:3} {'*' * percent}")

        else:
            # Report the actual sound area.
            min_percent = int(minimum / divisor)
            max_percent = int(maximum / divisor)
            bottom = max(min_percent - 1, 0)
            middle = min(max_percent - min_percent + 1, 100)
            top = 100 - bottom - middle

            info(f"{minimum:6} {maximum:6} |{' ' * bottom}{'*' * middle}{' ' * top}|")


    microphone_controller.add_handler(handle_sample)
    microphone_controller.start()

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + 10000000000000


    async def callback() -> None:
        runner.cancel = time.monotonic() > finish
        if runner.cancel:
            microphone_controller.stop()


    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    runner.run(callback)

    if REPORT_RAM:
        report_memory_usage_and_free("After running Runner")
