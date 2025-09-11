import time

from interactive.environment import are_pins_available, is_running_on_microcontroller
from interactive.log import set_log_level, INFO
from interactive.memory import report_memory_usage_and_free
from interactive.polyfills.animation import BLACK
from interactive.polyfills.pixel import new_pixels
from interactive.runner import Runner
from interactive.scheduler import new_scheduled_task

REPORT_RAM = is_running_on_microcontroller()

LED_YELLOW = None
LED_GREEN = None
LED_RED = None
PIXELS_PIN = None  # This is the single onboard NeoPixel connector
PIXELS_MULTI_PINS = None  # This is a list of all additional NeoPixel connectors on the board.

if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    PIXELS_PIN = board.GP15  # on a PlasmaStick

if __name__ == '__main__':

    set_log_level(INFO)

    if REPORT_RAM:
        report_memory_usage_and_free("Before creating Objects")

    runner = Runner()

    # See this example: https://learn.adafruit.com/easy-neopixel-graphics-with-the-circuitpython-pixel-framebuf-library
    from adafruit_pixel_framebuf import PixelFramebuffer, VERTICAL

    WIDTH = 20
    HEIGHT = 20

    pixels = new_pixels(PIXELS_PIN, WIDTH * HEIGHT, brightness=0.5)

    frame = PixelFramebuffer(
        pixels,
        WIDTH,
        HEIGHT,
        orientation=VERTICAL,
        alternating=False,
        rotation=0)

    screen = 0


    async def animate() -> None:
        global screen

        if not runner.cancel:

            if screen == 0:
                frame.fill(0x0000FF)
            elif screen == 1:
                frame.fill(0x00)
                frame.line(0, 0, 7, 9, 0xFFFF00)
                frame.rect(2, 2, 8, 12, 0x00FF00)
            else:
                frame.text("Hi", 10, 10, 0x0FFFF00)
            frame.display()

            screen += 1
            screen %= 3


    scheduled_task = new_scheduled_task(animate, frequency=1)
    runner.add_loop_task(scheduled_task)

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + 1000000


    async def callback() -> None:
        runner.cancel = time.monotonic() > finish
        if runner.cancel:
            pixels.fill(BLACK)
            pixels.write()


    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    runner.run(callback)

    if REPORT_RAM:
        report_memory_usage_and_free("After running Runner")
