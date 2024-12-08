import asyncio
import time
from random import randint, uniform

from interactive.animation import Flicker
from interactive.button import ButtonController
from interactive.environment import are_pins_available, is_running_on_microcontroller
from interactive.led import Led
from interactive.log import set_log_level, INFO, info
from interactive.memory import report_memory_usage_and_free
from interactive.polyfills.animation import BLACK, WHITE, AnimationSequence
from interactive.polyfills.animation import Blink, Pulse
from interactive.polyfills.button import new_button
from interactive.polyfills.led import new_led_pin
from interactive.polyfills.pixel import new_pixels
from interactive.runner import Runner
from interactive.scheduler import new_one_time_on_off_task

REPORT_RAM = is_running_on_microcontroller()

BUTTON_PIN = None
LED_YELLOW = None
LED_GREEN = None
LED_RED = None
PIXELS_PIN = None  # This is the single onboard NeoPixel connector

if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    BUTTON_PIN = board.GP27
    LED_YELLOW = board.GP6
    LED_GREEN = board.GP5
    LED_RED = board.GP1
    PIXELS_PIN = board.GP28

if __name__ == '__main__':

    set_log_level(INFO)

    if REPORT_RAM:
        report_memory_usage_and_free("Before creating Objects")

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


    async def lightning_on() -> None:
        pixels.fill(WHITE)
        pixels.brightness = uniform(0.1, 1.0)
        pixels.show()


    async def lightning_off() -> None:
        pixels.fill(BLACK)
        pixels.brightness = 0.0
        pixels.show()


    async def lightning_finish() -> None:
        await lightning_off()


    async def lightning_effect() -> None:
        info("Running lightning effect")
        lightning_task = new_one_time_on_off_task(
            cycles=randint(5, 15),
            on_duration_func=lambda: randint(5, 75) / 1000,
            off_duration_func=lambda: randint(35, 75) / 1000,
            on=lightning_on,
            off=lightning_off,
            finish=lightning_finish
        )
        await lightning_task()


    async def single_click_handler() -> None:
        info("Clicked")
        if not runner.cancel:
            # Run the lightning effect in a separate task.
            asyncio.create_task(lightning_effect())


    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_press_handler(single_click_handler)
    button_controller.register(runner)

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + 10


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

            pixels.fill(BLACK)
            pixels.write()


    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    runner.run(callback)

    if REPORT_RAM:
        report_memory_usage_and_free("After running Runner")
