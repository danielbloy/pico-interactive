import time

from interactive.animation import Flicker
from interactive.button import ButtonController
from interactive.environment import are_pins_available, is_running_on_microcontroller
from interactive.led import Led
from interactive.log import set_log_level, INFO
from interactive.memory import report_memory_usage_and_free
from interactive.polyfills.animation import AMBER, BLACK, WHITE, JADE, PINK, OLD_LACE, AnimationSequence
from interactive.polyfills.animation import AQUA, RED, GOLD, YELLOW, ORANGE, GREEN
from interactive.polyfills.animation import BLUE, CYAN, PURPLE, MAGENTA, TEAL
from interactive.polyfills.animation import ColorCycle, Sparkle, Rainbow, RainbowComet, RainbowChase
from interactive.polyfills.animation import RainbowSparkle, Blink, Chase, Pulse, Comet
from interactive.polyfills.button import new_button
from interactive.polyfills.led import new_led_pin
from interactive.polyfills.pixel import new_pixels
from interactive.runner import Runner

REPORT_RAM = is_running_on_microcontroller()

BUTTON_PIN = None
LED_YELLOW = None
LED_GREEN = None
LED_RED = None
PIXELS_PIN = None

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


    async def single_click_handler() -> None:
        if not runner.cancel and animation:
            animation.next()


    async def multi_click_handler() -> None:
        if not runner.cancel and animation:
            animation.previous()


    async def long_press_handler() -> None:
        if not runner.cancel and animation:
            animation.reset()


    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_click_handler(single_click_handler)
    button_controller.add_multi_click_handler(multi_click_handler)
    button_controller.add_long_press_handler(long_press_handler)
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

            animation.freeze()
            pixels.fill(BLACK)
            pixels.write()


    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    runner.run(callback)

    if REPORT_RAM:
        report_memory_usage_and_free("After running Runner")
