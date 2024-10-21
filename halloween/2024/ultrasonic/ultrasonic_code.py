import asyncio

from interactive.button import ButtonController
from interactive.configuration import BUTTON_PIN
from interactive.configuration import TRIGGER_DISTANCE, TRIGGER_DURATION
from interactive.configuration import ULTRASONIC_TRIGGER_PIN, ULTRASONIC_ECHO_PIN
from interactive.log import critical
from interactive.memory import setup_memory_reporting
from interactive.network import onboard_led, send_message
from interactive.polyfills.button import new_button
from interactive.polyfills.ultrasonic import new_ultrasonic
from interactive.runner import Runner
from interactive.ultrasonic import UltrasonicController

# Because of memory constraints, we do not use the Interactive class here.
# Rather, we setup everything ourselves to minimise what we pull in.
runner = Runner()

runner.cancel_on_exception = False
runner.restart_on_exception = True
runner.restart_on_completion = False


async def button_press() -> None:
    await trigger_handler(0, 0)


button_controller = ButtonController(new_button(BUTTON_PIN))
button_controller.add_single_press_handler(button_press)
button_controller.register(runner)


async def trigger_handler(distance: float, actual: float) -> None:
    critical(f"Distance {distance} handler triggered: {actual}")
    onboard_led.value = not onboard_led.value
    send_message("trigger")
    await asyncio.sleep(0.25)
    onboard_led.value = not onboard_led.value


ultrasonic = new_ultrasonic(ULTRASONIC_TRIGGER_PIN, ULTRASONIC_ECHO_PIN)
controller = UltrasonicController(ultrasonic)
controller.add_trigger(TRIGGER_DISTANCE, trigger_handler, TRIGGER_DURATION)
controller.register(runner)

setup_memory_reporting(runner)
runner.run()
