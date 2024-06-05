from adafruit_led_animation.sequence import AnimationSequence
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

from chrismas_songs import ALL_SONGS
from leds import LED
from music import AudioPin, Song, SongSequence
from neopixel import NeoPixel
from pixel_animations import Flicker
from songs import decode_song

import framework


def init(audio: AudioPin, red: LED, green: LED, yellow: LED, pixels: NeoPixel):
    # Music
    songs = []
    for song, speed in ALL_SONGS:
        songs.append(Song(audio, decode_song(song), speed))

    framework.music = SongSequence(*songs, loop=True)

    # LEDs
    framework.red_animation = Blink(red, speed=0.5, color=WHITE)
    framework.green_animation = Pulse(green, speed=0.1, color=WHITE, period=2)

    yellow_animations = [
        Flicker(yellow, speed=0.1, color=WHITE, spacing=1),
        Pulse(yellow, speed=0.1, color=WHITE, period=1),
        Blink(yellow, speed=0.5, color=WHITE),
    ]
    framework.yellow_animation = AnimationSequence(*yellow_animations, advance_interval=3, auto_clear=True)

    # NeoPixels
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
    framework.animation = AnimationSequence(*animations, advance_interval=5, auto_clear=True)
