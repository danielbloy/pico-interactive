import time

from interactive.button import ButtonController
from interactive.environment import are_pins_available, is_running_on_microcontroller
from interactive.log import set_log_level, INFO
from interactive.memory import report_memory_usage_and_free
from interactive.polyfills.animation import BLACK, PINK, GOLD, OLD_LACE, AnimationSequence
from interactive.polyfills.animation import Chase, Comet, Sparkle, RainbowComet, RainbowChase
from interactive.polyfills.button import new_button
from interactive.polyfills.pixel import new_pixels
from interactive.runner import Runner

REPORT_RAM = is_running_on_microcontroller()

BUTTON_PIN = None
LED_YELLOW = None
LED_GREEN = None
LED_RED = None
PIXELS_PIN = None  # This is the single onboard NeoPixel connector
PIXELS_MULTI_PINS = None  # This is a list of all additional NeoPixel connectors on the board.

if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    BUTTON_PIN = board.BUTTON
    PIXELS_PIN = board.GP15  # on a PlasmaStick

if __name__ == '__main__':

    set_log_level(INFO)

    if REPORT_RAM:
        report_memory_usage_and_free("Before creating Objects")

    runner = Runner()

    # See this example: https://learn.adafruit.com/circuitpython-led-animations/pixel-mapping
    from adafruit_pixelmap import PixelMap, horizontal_strip_gridmap

    pixels = new_pixels(PIXELS_PIN, 400, brightness=0.5)

    pixels_vertical = PixelMap.vertical_lines(
        pixels, 20, 20, horizontal_strip_gridmap(20, alternating=False)
    )
    pixels_horizontal = PixelMap.horizontal_lines(
        pixels, 20, 20, horizontal_strip_gridmap(20, alternating=False)
    )

    animations = [
        Comet(pixels_vertical, speed=0.01, color=PINK, tail_length=7, bounce=True),
        Chase(pixels_horizontal, speed=0.1, size=3, spacing=6, color=OLD_LACE),
        Sparkle(pixels, speed=0.05, color=GOLD, num_sparkles=3),
        RainbowComet(pixels_vertical, speed=0.1, tail_length=7, bounce=True),
        RainbowChase(pixels_horizontal, speed=0.1, size=5),
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
    button_controller.add_single_press_handler(single_click_handler)
    button_controller.add_multi_press_handler(multi_click_handler)
    button_controller.add_long_press_handler(long_press_handler)
    button_controller.register(runner)

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + 1000000


    async def callback() -> None:
        runner.cancel = time.monotonic() > finish
        if runner.cancel:
            animation.freeze()
            pixels.fill(BLACK)
            pixels.write()


    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    runner.run(callback)

    if REPORT_RAM:
        report_memory_usage_and_free("After running Runner")
