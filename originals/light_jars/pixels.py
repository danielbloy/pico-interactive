import asyncio
import clock

__pixelsEnabled: bool = False


async def execute():
    from environment import isBlinkaAvailable
    if not isBlinkaAvailable:
        return

    from adafruit_led_animation.animation import Animation
    from adafruit_led_animation.animation.blink import Blink
    from adafruit_led_animation.animation.comet import Comet
    from adafruit_led_animation.animation.chase import Chase
    from adafruit_led_animation.animation.colorcycle import ColorCycle
    from adafruit_led_animation.animation.pulse import Pulse
    from adafruit_led_animation.animation.sparkle import Sparkle
    from adafruit_led_animation.animation.rainbow import Rainbow
    from adafruit_led_animation.animation.rainbowchase import RainbowChase
    from adafruit_led_animation.animation.rainbowcomet import RainbowComet
    from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle
    from adafruit_led_animation.color import RED, YELLOW, ORANGE, GREEN, TEAL, CYAN
    from adafruit_led_animation.color import BLUE, PURPLE, MAGENTA, WHITE, BLACK
    from adafruit_led_animation.color import GOLD, PINK, AQUA, JADE, AMBER, OLD_LACE
    from adafruit_led_animation.sequence import AnimationSequence

    from config import SLEEP_INTERVAL
    from config import PIXELS_PIN, PIXELS_NODES_NUM, PIXELS_PER_NODE
    from config import PIXELS_ON, PIXELS_BRIGHTNESS, PIXELS_SPEED, PIXELS_ON_TIME, PIXEL_OFF_TIME
    from config import ANIMATION_DURATION, ANIMATIONS
    from flicker import Flicker
    from neopixel import NeoPixel

    # PIXELS_SPEED should be a value from zero to 1.0 (which is enforced). We use Zero as slowest and 1
    # as the fastest value. However, for the animations we need to switch it around.
    speed: float = 1.0 - max(0.0, min(1.0, PIXELS_SPEED))
    total_pixels: int = PIXELS_NODES_NUM * PIXELS_PER_NODE
    pixels: NeoPixel = NeoPixel(PIXELS_PIN, total_pixels, brightness=PIXELS_BRIGHTNESS, auto_write=False)
    pixels.fill(BLACK)
    pixels.write()

    # These are the default in-built animations
    animations_library: dict[str, Animation] = {
        "flicker": Flicker(pixels, speed=speed, color=GREEN, spacing=1),
        "blink": Blink(pixels, speed=speed, color=JADE),
        "comet": Comet(pixels, speed=speed, color=GREEN, tail_length=7, bounce=True),
        "chase": Chase(pixels, speed=speed, size=5, spacing=3, color=OLD_LACE),
        "cycle": ColorCycle(pixels, speed=speed, colors=[RED, YELLOW, ORANGE, GREEN, CYAN, BLUE, PURPLE, MAGENTA]),
        "pulse": Pulse(pixels, speed=speed, color=GREEN, period=3),
        "sparkle": Sparkle(pixels, speed=speed, color=GOLD, num_sparkles=3),
        "rainbow": Rainbow(pixels, speed=speed, period=2),
        "rainbow_comet": RainbowComet(pixels, speed=speed, tail_length=7, bounce=True),
        "rainbow_chase": RainbowChase(pixels, speed=0.01, size=2, spacing=4),
        "rainbow_sparkle": RainbowSparkle(pixels, speed=speed, num_sparkles=3),
    }

    # Generate the list of animation names based on the configuration.
    if ANIMATIONS:
        animations = [animation_name for animation_name in animations_library if animation_name in ANIMATIONS]
    else:
        animations = [animation_name for animation_name in animations_library]

    # Convert the names into an animation playlist.
    playlist = [animations_library[animation_name] for animation_name in animations]

    # If there are no animations in the playlist (because they were spelt incorrectly) then add
    # a blink animation that is always off.
    if not animations:
        playlist = [Blink(pixels, speed=speed, color=BLACK)]

    # If there is only a single animation in the playlist then we use an interval of zero to avoid interrupting it.
    animation: AnimationSequence = (
        AnimationSequence(*playlist, auto_clear=True,
                          advance_interval=(0 if len(playlist) == 1 else ANIMATION_DURATION)))

    async def animate_pixels():
        global __pixelsEnabled
        while True:
            if __pixelsEnabled:
                if animation:
                    animation.animate()
                await asyncio.sleep(SLEEP_INTERVAL / 1000)
            else:
                pixels.fill(BLACK)
                pixels.write()
                await asyncio.sleep(5)

    async def enable_pixels():
        global __pixelsEnabled

        on_hour = PIXELS_ON_TIME // 100
        off_hour = PIXEL_OFF_TIME // 100
        on_minute = PIXELS_ON_TIME % 100
        off_minute = PIXEL_OFF_TIME % 100
        print(f"Pixels on time: {on_hour:02}:{on_minute:02}")
        print(f"Pixels off time: {off_hour:02}:{off_minute:02}")

        while True:
            state = False
            if PIXELS_ON:
                lt = clock.get_clock()
                if on_hour <= lt.tm_hour <= off_hour:
                    # We only need concern ourselves with the minutes if in either the on_hour or off_hour
                    if lt.tm_hour != on_hour and lt.tm_hour != off_hour:
                        state = True
                    else:
                        if on_hour == lt.tm_hour == off_hour:
                            state = on_minute <= lt.tm_min < off_minute
                        elif lt.tm_hour == on_hour:
                            state = lt.tm_min >= on_minute
                        else:
                            state = lt.tm_min < off_minute

            __pixelsEnabled = state

            await asyncio.sleep(5)

    tasks: list[asyncio.Task] = [asyncio.create_task(enable_pixels()), asyncio.create_task(animate_pixels())]

    await asyncio.gather(*tasks)
