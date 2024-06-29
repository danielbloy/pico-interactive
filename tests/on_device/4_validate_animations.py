import time

from framework.animation import AMBER, BLACK
from framework.button import ButtonController
from framework.environment import are_pins_available
from framework.log import set_log_level, INFO
from framework.pixel import Flicker
from framework.polyfills.button import new_button
from framework.polyfills.pixel import new_pixels
from framework.runner import Runner

BUTTON_PIN = None
PIXELS_PIN = None
LED_RED = None
LED_YELLOW = None
LED_GREEN = None

if are_pins_available():
    import board

    BUTTON_PIN = board.GP27
    PIXELS_PIN = board.GP28

if __name__ == '__main__':
    # Allow the application to only run for a defined number of seconds.
    start = time.monotonic()
    finish = start + 10

    set_log_level(INFO)

    pixels = new_pixels(PIXELS_PIN, 8, brightness=0.2)
    animation = Flicker(pixels, speed=0.1, color=AMBER, spacing=2)


    async def animate_pixels() -> None:
        animation.animate()


    async def callback() -> None:
        global start, finish
        runner.cancel = time.monotonic() > finish
        if runner.cancel:
            animation.freeze()  # TODO: This should be animations.off() when implemented
            pixels.fill(BLACK)
            pixels.write()


    async def single_click_handler() -> None:
        # Move to the next animation in the sequence
        pass


    async def multi_click_handler() -> None:
        # Either pause or resume the pixel animations
        pass


    async def long_press_handler() -> None:
        # Either turn on or off the LEDs
        pass


    runner = Runner()

    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_click_handler(single_click_handler)
    button_controller.add_multi_click_handler(multi_click_handler)
    button_controller.add_long_press_handler(long_press_handler)
    button_controller.register(runner)

    runner.add_loop_task(animate_pixels)

    runner.run(callback)