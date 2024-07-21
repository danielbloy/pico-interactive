# Entry point for a path node. This supports both path nodes that are on either
# side of the path. One will be the primary node and the other the secondary.
from interactive.animation import Flicker
from interactive.environment import are_pins_available
from interactive.interactive import Interactive
from interactive.log import set_log_level, info, INFO
from interactive.polyfills.animation import AMBER, BLACK
from interactive.polyfills.pixel import new_pixels

PRIMARY = True
BUTTON_PIN = None
BUZZER_PIN = None
BUZZER_VOLUME = 0.1
SKULL_BRIGHTNESS = 1.0
SKULL_SPEED = 0.1
SKULL_COLOUR = AMBER
SKULL_PINS = [None, None, None, None, None, None]

# Default settings
if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    BUTTON_PIN = board.GP27
    BUZZER_PIN = board.GP2

    SKULL_PINS = [board.GP10, board.GP11, board.GP12, board.GP13, board.GP14, board.GP15]

if __name__ == '__main__':

    set_log_level(INFO)

    # Try loading local device settings as overrides.
    try:
        # noinspection PyPackageRequirements
        from config import *

        info("Config file loaded")

    except ImportError:
        info("No config file was found")

    config = Interactive.Config()
    config.buzzer_pin = BUZZER_PIN
    config.button_pin = BUTTON_PIN
    config.buzzer_volume = BUZZER_VOLUME

    interactive = Interactive(config)

    # Construct the pixels and animate them.
    pixels = [new_pixels(pin, 8, brightness=SKULL_BRIGHTNESS) for pin in SKULL_PINS if pin is not None]
    animations = [Flicker(pixel, speed=SKULL_SPEED, color=SKULL_COLOUR) for pixel in pixels]


    async def animate_skulls() -> None:
        for animation in animations:
            animation.animate()


    interactive.runner.add_loop_task(animate_skulls)


    # TODO: Control how the skulls are enabled/disabled.

    async def callback() -> None:
        if interactive.cancel:
            for animation in animations:
                animation.freeze()

            for pixel in pixels:
                pixel.fill(BLACK)
                pixel.write()


    interactive.run(callback)
