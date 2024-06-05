from adafruit_led_animation.animation import Animation
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
    notes = [
        "C4:1", "D:1", "E:1", "F:1", "G:1", "A:1", "B:1", "C5:1",
        "B4:1", "A:1", "G:1", "F:1", "E:1", "D:1", "C:1"]
    song = Song(audio, decode_song(notes), 0.2)
    framework.music = SongSequence(song, loop=True)

    framework.yellow_animation = Flicker(yellow, speed=0.1, color=WHITE, spacing=1)
    framework.animation = Comet(pixels, speed=0.01, color=PINK, tail_length=7, bounce=True)


# Execute the script proper using the framework.
from framework import run
run(init)
