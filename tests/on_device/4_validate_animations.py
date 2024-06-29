import time

from interactive.animation import AMBER, BLACK, WHITE
from interactive.button import ButtonController
from interactive.environment import are_pins_available
from interactive.led import Led
from interactive.log import set_log_level, INFO
from interactive.pixel import Flicker
from interactive.polyfills.button import new_button
from interactive.polyfills.led import new_led_pin
from interactive.polyfills.pixel import new_pixels
from interactive.runner import Runner

BUTTON_PIN = None
LED_YELLOW = None
LED_GREEN = None
LED_RED = None
PIXELS_PIN = None

if are_pins_available():
    import board

    BUTTON_PIN = board.GP27
    LED_YELLOW = board.GP6
    LED_GREEN = board.GP5
    LED_RED = board.GP1
    PIXELS_PIN = board.GP28

if __name__ == '__main__':
    # Allow the application to only run for a defined number of seconds.
    start = time.monotonic()
    finish = start + 10

    set_log_level(INFO)

    yellow = Led(new_led_pin(LED_YELLOW))
    yellow_animation = Flicker(yellow, speed=0.1, color=WHITE)

    green = Led(new_led_pin(LED_GREEN))
    green_animation = Flicker(green, speed=0.1, color=WHITE)

    red = Led(new_led_pin(LED_RED))
    red_animation = Flicker(red, speed=0.1, color=WHITE)

    pixels = new_pixels(PIXELS_PIN, 8, brightness=0.2)
    animation = Flicker(pixels, speed=0.1, color=AMBER, spacing=2)


    async def animate() -> None:
        yellow_animation.animate()
        green_animation.animate()
        red_animation.animate()
        animation.animate()


    async def callback() -> None:
        global start, finish
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

    runner.add_loop_task(animate)

    runner.run(callback)
