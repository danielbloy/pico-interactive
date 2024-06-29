# This tests the button and buzzer functionality on the basic Code Club
# Christmas board.
import time

# TODO: We want these references to go
from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.chase import Chase
from adafruit_led_animation.animation.colorcycle import ColorCycle
from adafruit_led_animation.animation.comet import Comet
from adafruit_led_animation.animation.pulse import Pulse
from adafruit_led_animation.animation.rainbow import Rainbow
from adafruit_led_animation.animation.rainbowchase import RainbowChase
from adafruit_led_animation.animation.rainbowcomet import RainbowComet
from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle
from adafruit_led_animation.animation.sparkle import Sparkle
from adafruit_led_animation.sequence import AnimationSequence

from chrismas_songs import ALL_SONGS
from interactive.animation import AMBER, BLACK, WHITE, JADE, PINK, OLD_LACE
from interactive.animation import RED, AQUA, GOLD, YELLOW, ORANGE, GREEN
from interactive.animation import TEAL, CYAN, BLUE, PURPLE, MAGENTA
from interactive.button import ButtonController
from interactive.environment import are_pins_available
from interactive.led import Led
from interactive.log import set_log_level, INFO
from interactive.melody import Melody, decode_melody, MelodySequence
from interactive.pixel import Flicker
from interactive.polyfills.button import new_button
from interactive.polyfills.buzzer import new_buzzer
from interactive.polyfills.led import new_led_pin
from interactive.polyfills.pixel import new_pixels
from interactive.runner import Runner

AUDIO_PIN = None
BUTTON_PIN = None
LED_YELLOW = None
LED_GREEN = None
LED_RED = None
PIXELS_PIN = None

# Audio configuration
PLAY_SONGS = True
AUDIO_VOLUME = 0.1

# LED configuration
ANIMATE_LEDS = True

# Neopixel configuration
ANIMATE_PIXELS = True
PIXELS_BRIGHTNESS = 0.2

# Demo mode configuration
DEMO_MODE = True

if are_pins_available():
    import board

    AUDIO_PIN = board.GP2  # or GP3
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

    runner = Runner()

    audio = new_buzzer(AUDIO_PIN)
    audio.volume = AUDIO_VOLUME
    songs = []
    for song, speed in ALL_SONGS:
        songs.append(Melody(audio, decode_melody(song), speed))

    songs = MelodySequence(*songs, loop=True)


    async def play_songs() -> None:
        if not runner.cancel and PLAY_SONGS:
            if songs:
                songs.play()


    runner.add_loop_task(play_songs)

    yellow = Led(new_led_pin(LED_YELLOW))
    green = Led(new_led_pin(LED_GREEN))
    red = Led(new_led_pin(LED_RED))

    red_animation = Blink(red, speed=0.5, color=WHITE)
    green_animation = Pulse(green, speed=0.1, color=WHITE, period=2)

    yellow_animations = [
        Flicker(yellow, speed=0.1, color=WHITE, spacing=1),
        Pulse(yellow, speed=0.1, color=WHITE, period=1),
        Blink(yellow, speed=0.5, color=WHITE),
    ]
    yellow_animation = AnimationSequence(*yellow_animations, advance_interval=3, auto_clear=True)


    async def animate_leds() -> None:
        if not runner.cancel and ANIMATE_LEDS:
            if red_animation:
                red_animation.animate()
            if green_animation:
                green_animation.animate()
            if yellow_animation:
                yellow_animation.animate()


    runner.add_loop_task(animate_leds)

    pixels = new_pixels(PIXELS_PIN, 8, brightness=PIXELS_BRIGHTNESS)
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
        RainbowChase(pixels, speed=0.1, size=5, spacing=3),
        RainbowSparkle(pixels, speed=0.1, num_sparkles=3),
    ]
    animation = AnimationSequence(*animations, advance_interval=5, auto_clear=True)


    async def animate_pixels() -> None:
        if not runner.cancel and ANIMATE_PIXELS:
            if animation:
                animation.animate()


    runner.add_loop_task(animate_pixels)


    async def callback() -> None:
        global start, finish
        runner.cancel = time.monotonic() > finish
        if runner.cancel:
            audio.off()

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


    async def single_click_handler() -> None:
        # Move to the next animation in the sequence
        if songs:
            if songs.paused:
                songs.resume()
            else:
                songs.pause()


    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_click_handler(single_click_handler)
    button_controller.register(runner)

    runner.run(callback)
