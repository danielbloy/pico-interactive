# This script is designed to be run on the device and tests all functionality
# to ensure compatibility. This is designed to be run on a board that has
# a button, buzzer, LEDs, NeoPixels and Wifi. It does test the ultrasonic
#
# Each item is done once at a time in the following order with each section
# taking a small amount of time (RAM details will be output at each point and
# the logger functionality will be used throughout):
# 1. Runner with Wifi,
# 2. Runner with button and buzzer (melodies)
# 3. Runner with LEDs, NeoPixels and animations
# 4. Runner with audio (MP3) through buzzer
# 5. Runner with ultrasonic sensor
# 6. Interactive framework (limited in functionality to conserve RAM).

import time

from interactive.button import ButtonController
from interactive.configuration import AUDIO_PIN, BUTTON_PIN, BUZZER_PIN, get_node_config
from interactive.configuration import ULTRASONIC_TRIGGER_PIN, ULTRASONIC_ECHO_PIN, TRIGGER_DISTANCE, TRIGGER_DURATION
from interactive.environment import are_pins_available, is_running_on_microcontroller
from interactive.log import set_log_level, info, INFO
from interactive.memory import report_memory_usage_and_free
from interactive.polyfills.button import new_button
from interactive.runner import Runner

STEP_RUN_TIME = 5

REPORT_RAM = is_running_on_microcontroller()  # Override

steps = []

AUDIO_FILE = "lion.mp3"

LED_YELLOW = None
LED_GREEN = None
LED_RED = None

PIXELS_PIN = None  # This is the single onboard NeoPixel connector

if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    # Defaults in the absence of configuration options
    if not AUDIO_PIN:
        AUDIO_PIN = board.GP2

    if not BUTTON_PIN:
        BUTTON_PIN = board.GP27

    if not BUZZER_PIN:
        BUZZER_PIN = board.GP2

    if not ULTRASONIC_TRIGGER_PIN:
        ULTRASONIC_TRIGGER_PIN = board.GP7

    if not ULTRASONIC_ECHO_PIN:
        ULTRASONIC_ECHO_PIN = board.GP6

    if not TRIGGER_DISTANCE:
        TRIGGER_DISTANCE = 30

    if not TRIGGER_DURATION:
        TRIGGER_DURATION = 1

    LED_YELLOW = board.GP6
    LED_GREEN = board.GP5
    LED_RED = board.GP1

    PIXELS_PIN = board.GP28


# ********************************************************************************
# STEP 1: Runner with WiFi
# ********************************************************************************
def runner_with_wifi() -> None:
    from interactive.network import NetworkController, send_message
    from interactive.polyfills.network import new_server

    if REPORT_RAM:
        report_memory_usage_and_free("Before executing runner_with_wifi")

    async def single_click_handler() -> None:
        info('Single click!')

    runner = Runner()

    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_press_handler(single_click_handler)
    button_controller.register(runner)

    server = new_server(debug=False)
    network_controller = NetworkController(server)
    network_controller.register(runner)

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + STEP_RUN_TIME

    async def callback() -> None:
        runner.cancel = time.monotonic() > finish

    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    runner.run(callback)

    del network_controller, server, button_controller, button, runner

    # Send message to get the quote from adafruit quotes
    response = send_message("/api/quotes.php", "www.adafruit.com", "https")
    info(response.text)
    response.close()

    if REPORT_RAM:
        report_memory_usage_and_free("After executing runner_with_wifi")


steps.append({"name": "Runner with WiFi", "func": runner_with_wifi})


# ********************************************************************************
# STEP 2: Runner with Button and Buzzer (plays a melody)
# ********************************************************************************
def runner_with_button_and_buzzer() -> None:
    from interactive.buzzer import BuzzerController
    from interactive.melody import MelodySequence, Melody, decode_melody
    from interactive.polyfills.buzzer import new_buzzer
    from interactive.polyfills.led import onboard_led

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
    finish = time.monotonic() + STEP_RUN_TIME

    async def callback() -> None:
        runner.cancel = time.monotonic() > finish

    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    runner.run(callback)

    del buzzer_controller, melody, buzzer, button_controller, button, runner

    if REPORT_RAM:
        report_memory_usage_and_free("After executing runner_with_button_and_buzzer")


steps.append({"name": "Runner with button and buzzer", "func": runner_with_button_and_buzzer})


# ********************************************************************************
# STEP 3: Runner with LEDs, NeoPixels and animations.
# ********************************************************************************
def runner_with_leds_pixels_animations() -> None:
    from interactive.animation import Flicker
    from interactive.led import Led
    from interactive.polyfills.animation import AMBER, BLACK, WHITE, JADE, PINK, OLD_LACE, AnimationSequence
    from interactive.polyfills.animation import AQUA, RED, GOLD, YELLOW, ORANGE, GREEN
    from interactive.polyfills.animation import BLUE, CYAN, PURPLE, MAGENTA, TEAL
    from interactive.polyfills.animation import ColorCycle, Sparkle, Rainbow, RainbowComet, RainbowChase
    from interactive.polyfills.animation import RainbowSparkle, Blink, Chase, Pulse, Comet
    from interactive.polyfills.led import new_led_pin
    from interactive.polyfills.pixel import new_pixels

    if REPORT_RAM:
        report_memory_usage_and_free("Before executing runner_with_leds_pixels_animations")

    runner = Runner()

    yellow = Led(new_led_pin(LED_YELLOW))
    green = Led(new_led_pin(LED_GREEN))
    red = Led(new_led_pin(LED_RED))

    red_animation = Blink(red, speed=0.5, color=WHITE)
    green_animation = Pulse(green, speed=0.1, color=WHITE, period=2)

    yellow_animations = [
        Flicker(yellow, speed=0.1, color=WHITE),
        Pulse(yellow, speed=0.1, color=WHITE, period=1),
        Blink(yellow, speed=0.5, color=WHITE),
    ]
    yellow_animation = AnimationSequence(*yellow_animations, advance_interval=3)

    async def animate_leds() -> None:
        if not runner.cancel:
            if red_animation:
                red_animation.animate()
            if green_animation:
                green_animation.animate()
            if yellow_animation:
                yellow_animation.animate()

    runner.add_loop_task(animate_leds)

    pixels = new_pixels(PIXELS_PIN, 8, brightness=0.5)
    animations = [
        Flicker(pixels, speed=0.1, color=AMBER, spacing=2),
        Blink(pixels, speed=0.5, color=JADE),
        Comet(pixels, speed=0.01, color=PINK, tail_length=7, bounce=True),
        Chase(pixels, speed=0.1, size=3, spacing=6, color=OLD_LACE),
        ColorCycle(pixels, 0.5, colors=[RED, YELLOW, ORANGE, GREEN, TEAL, CYAN, BLUE, PURPLE, MAGENTA, BLACK]),
        Pulse(pixels, speed=0.1, color=AQUA, period=3),
        Sparkle(pixels, speed=0.05, color=GOLD, num_sparkles=3),
        Rainbow(pixels, speed=0.1, period=2),
        RainbowComet(pixels, speed=0.1, tail_length=7, bounce=True),
        RainbowChase(pixels, speed=0.1, size=5),
        RainbowSparkle(pixels, speed=0.1, num_sparkles=3),
    ]
    animation = AnimationSequence(*animations, advance_interval=5)

    async def animate_pixels() -> None:
        if not runner.cancel:
            if animation:
                animation.animate()

    runner.add_loop_task(animate_pixels)

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + STEP_RUN_TIME

    async def callback() -> None:
        runner.cancel = time.monotonic() > finish
        if runner.cancel:
            yellow_animation.freeze()
            green_animation.freeze()
            red_animation.freeze()

            yellow.off()
            green.off()
            red.off()
            yellow.show()
            green.show()
            red.show()

            animation.freeze()
            pixels.fill(BLACK)
            pixels.write()

    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    runner.run(callback)

    del animation, animations, pixels, yellow_animations, yellow_animation, green_animation, red_animation
    del red, green, yellow, runner

    if REPORT_RAM:
        report_memory_usage_and_free("After executing runner_with_leds_pixels_animations")


steps.append({"name": "Runner with LEDs, pixels and animations", "func": runner_with_leds_pixels_animations})


# ********************************************************************************
# STEP 4: Runner with Audio (MP3s) through Buzzer.
# ********************************************************************************
def runner_with_mp3_audio() -> None:
    from interactive.audio import AudioController
    from interactive.polyfills.audio import new_mp3_player

    if REPORT_RAM:
        report_memory_usage_and_free("Before executing runner_with_mp3_audio")

    async def single_click_handler() -> None:
        info('Single click!')
        audio_controller.queue(AUDIO_FILE)

    runner = Runner()

    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_press_handler(single_click_handler)
    button_controller.register(runner)

    audio = new_mp3_player(AUDIO_PIN, AUDIO_FILE)
    audio_controller = AudioController(audio)
    audio_controller.register(runner)

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + STEP_RUN_TIME

    async def callback() -> None:
        runner.cancel = time.monotonic() > finish

    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    runner.run(callback)

    del audio_controller, audio, button_controller, button, runner

    if REPORT_RAM:
        report_memory_usage_and_free("After executing runner_with_mp3_audio")


steps.append({"name": "Runner with MP3 audio", "func": runner_with_mp3_audio})


# ********************************************************************************
# STEP 5: Runner with Ultrasonic sensor.
# ********************************************************************************
def runner_with_ultrasonic_sensor() -> None:
    from interactive.polyfills.ultrasonic import new_ultrasonic
    from interactive.ultrasonic import UltrasonicController

    if REPORT_RAM:
        report_memory_usage_and_free("Before executing runner_with_ultrasonic_sensor")

    async def single_click_handler() -> None:
        info(f"Distance: {ultrasonic.distance}")

    async def trigger_handler(distance: float, actual: float) -> None:
        info(f"Distance {distance} handler triggered: {actual}")

    runner = Runner()

    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_press_handler(single_click_handler)
    button_controller.register(runner)

    ultrasonic = new_ultrasonic(ULTRASONIC_TRIGGER_PIN, ULTRASONIC_ECHO_PIN)
    ultrasonic_controller = UltrasonicController(ultrasonic)
    ultrasonic_controller.add_trigger(TRIGGER_DISTANCE, trigger_handler, TRIGGER_DURATION)
    ultrasonic_controller.register(runner)

    async def trigger_handler(distance: float, actual: float) -> None:
        info(f"Distance {distance} handler triggered: {actual}")

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + STEP_RUN_TIME

    async def callback() -> None:
        runner.cancel = time.monotonic() > finish

    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    runner.run(callback)

    del ultrasonic_controller, ultrasonic, button_controller, button, runner

    if REPORT_RAM:
        report_memory_usage_and_free("After executing runner_with_ultrasonic_sensor")


steps.append({"name": "Runner with ultrasonic sensor", "func": runner_with_ultrasonic_sensor})


# ********************************************************************************
# STEP 6: Interactive framework (limited functionality due to RAM constraints).
# ********************************************************************************
def runner_with_interactive_framework() -> None:
    from interactive.framework import Interactive

    if REPORT_RAM:
        report_memory_usage_and_free("Before executing runner_with_interactive_framework")

    async def trigger_start() -> None:
        info('Trigger start!')

    config = get_node_config()
    config.trigger_start = trigger_start
    interactive = Interactive(config)

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + STEP_RUN_TIME

    async def callback() -> None:
        interactive.cancel = time.monotonic() > finish

    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    interactive.run(callback)

    del interactive, config

    if REPORT_RAM:
        report_memory_usage_and_free("After executing runner_with_interactive_framework")


steps.append({"name": "Runner with interactive framework", "func": runner_with_interactive_framework})

# Execute each step in turn to test the device.
if __name__ == '__main__':
    set_log_level(INFO)

    for idx, step in enumerate(steps):
        print(f"Running step {idx + 1}: {step["name"]}")
        step["func"]()
