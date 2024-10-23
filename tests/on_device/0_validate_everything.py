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
# 2. TODO: Runner with button and buzzer (melodies)
# 3. TODO: Runner with LEDs, NeoPixels and animations
# 4. TODO: Runner with audio (MP3s) through buzzer
# 5. TODO: Runner with ultrasonic sensor
# 6. TODO: Interactive framework (limited in functionality to conserve RAM).

from interactive.environment import is_running_on_microcontroller
from interactive.log import set_log_level, INFO

REPORT_RAM = is_running_on_microcontroller()

steps = []


# ********************************************************************************
# STEP 1: Runner with WiFi
# ********************************************************************************
def runner_with_wifi() -> None:
    pass


steps.append({"name": "Runner with WiFi", "func": runner_with_wifi})


# ********************************************************************************
# STEP 2: Runner with Button and Buzzer.
# ********************************************************************************
def runner_with_button_and_buzzer() -> None:
    pass


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
