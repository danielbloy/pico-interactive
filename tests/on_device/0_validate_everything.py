# This script is designed to be run on the device and tests all functionality
# to ensure compatibility. This is designed to be run on a board that has
# a button, buzzer, LEDs, NeoPixels and Wifi. It does test the ultrasonic
#
# Each item is done once at a time in the following order with each section
# taking a small amount of time (RAM details will be output at each point and
# the logger functionality will be used throughout):
# 1. Runner with Wifi,
#  1a. TODO: Send and receive messages
#  1b. TODO: Directory
# 2. Runner with button and buzzer (melodies)
# 3. Runner with LEDs, NeoPixels and animations
# 4. TODO: Runner with audio (MP3s) through buzzer
# 5. TODO: Runner with ultrasonic sensor
# 6. TODO: Interactive framework (limited in functionality to conserve RAM).

import time

from buzzer import BuzzerController
from interactive.button import ButtonController
from interactive.directory import DirectoryService
from interactive.environment import are_pins_available, is_running_on_microcontroller
from interactive.log import set_log_level, info, INFO
from interactive.memory import report_memory_usage_and_free
from interactive.network import NetworkController
from interactive.polyfills.button import new_button
from interactive.polyfills.led import onboard_led
from interactive.polyfills.network import new_server
from interactive.runner import Runner
from melody import MelodySequence, Melody, decode_melody
from polyfills.buzzer import new_buzzer

REPORT_RAM = is_running_on_microcontroller()

steps = []

BUTTON_PIN = None
BUZZER_PIN = None

LED_YELLOW = None
LED_GREEN = None
LED_RED = None
PIXELS_PIN = None  # This is the single onboard NeoPixel connector

if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    BUTTON_PIN = board.GP27
    BUZZER_PIN = board.GP2

    LED_YELLOW = board.GP6
    LED_GREEN = board.GP5
    LED_RED = board.GP1
    PIXELS_PIN = board.GP28


# ********************************************************************************
# STEP 1: Runner with WiFi
# ********************************************************************************
def runner_with_wifi() -> None:
    if REPORT_RAM:
        report_memory_usage_and_free("Before executing runner_with_wifi")

    led = onboard_led()

    async def single_click_handler() -> None:
        info('Single click!')
        led.value = not led.value

    runner = Runner()

    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_press_handler(single_click_handler)
    button_controller.register(runner)

    server = new_server(debug=False)
    network_controller = NetworkController(server)
    network_controller.register(runner)
    directory = DirectoryService()
    network_controller.server.add_routes(directory.get_routes())
    directory.register(runner)

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + 5

    async def callback() -> None:
        runner.cancel = time.monotonic() > finish

    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    runner.run(callback)

    del directory, network_controller, server, button_controller, button, runner

    if REPORT_RAM:
        report_memory_usage_and_free("After executing runner_with_wifi")


steps.append({"name": "Runner with WiFi", "func": runner_with_wifi})


# ********************************************************************************
# STEP 2: Runner with Button and Buzzer.
# ********************************************************************************
def runner_with_button_and_buzzer() -> None:
    if REPORT_RAM:
        report_memory_usage_and_free("Before executing runner_with_button_and_buzzer")

    led = onboard_led()

    async def single_click_handler() -> None:
        info('Single click!')
        led.value = not led.value
        buzzer_controller.beeps(3)

    async def multi_click_handler() -> None:
        info('Multi click!')
        if melody.paused:
            melody.resume()
        else:
            melody.pause()

    async def long_press_handler() -> None:
        info('Long press!')
        melody.reset()

    runner = Runner()

    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_press_handler(single_click_handler)
    button_controller.add_multi_press_handler(multi_click_handler)
    button_controller.add_long_press_handler(long_press_handler)
    button_controller.register(runner)

    notes = [
        "C4:1", "D:1", "E:1", "F:1", "G:1", "A:1", "B:1", "C5:1",
        "B4:1", "A:1", "G:1", "F:1", "E:1", "D:1", "C:1"]

    buzzer = new_buzzer(BUZZER_PIN)
    buzzer.volume = 0.1
    melody = MelodySequence(Melody(buzzer, decode_melody(notes), 0.2))
    melody.pause()

    async def play_melody() -> None:
        if not runner.cancel:
            melody.play()

    buzzer_controller = BuzzerController(buzzer)
    buzzer_controller.register(runner)
    runner.add_loop_task(play_melody)

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + 5

    async def callback() -> None:
        runner.cancel = time.monotonic() > finish

    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    runner.run(callback)

    del buzzer_controller, melody, buzzer, button_controller, button, runner

    if REPORT_RAM:
        report_memory_usage_and_free("After executing runner_with_button_and_buzzer")


steps.append({"name": "Runner with button and buzzer", "func": runner_with_button_and_buzzer()})


# ********************************************************************************
# STEP 3: Runner with LEDs, NeoPixels and animations.
# ********************************************************************************
def runner_with_leds_pixels_animations() -> None:
    pass


steps.append({"name": "Runner with LEDs, pixels and animations", "func": runner_with_leds_pixels_animations})


# ********************************************************************************
# STEP 4: Runner with Audio (MP3s) through Buzzer.
# ********************************************************************************
def runner_with_mp3_audio() -> None:
    pass


steps.append({"name": "Runner with MP3 audio", "func": runner_with_mp3_audio})


# ********************************************************************************
# STEP 5: Runner with Ultrasonic sensor.
# ********************************************************************************
def runner_with_ultrasonic_sensor() -> None:
    pass


steps.append({"name": "Runner with ultrasonic sensor", "func": runner_with_ultrasonic_sensor})


# ********************************************************************************
# STEP 6: Interactive framework (limited functionality due to RAM constraints).
# ********************************************************************************
def runner_with_interactive_framework() -> None:
    pass


steps.append({"name": "Runner with interactive framework", "func": runner_with_interactive_framework})

# Execute each step in turn to test the device.
if __name__ == '__main__':
    set_log_level(INFO)

    for idx, step in enumerate(steps):
        print(f"Running step {idx + 1}: {step["name"]}")
