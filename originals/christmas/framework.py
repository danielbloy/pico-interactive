import asyncio
import digitalio
import demo

from adafruit_debouncer import Debouncer
from adafruit_led_animation.animation import Animation
from adafruit_led_animation.color import BLACK

# Import configuration
from config import BUTTON_PIN, AUDIO_PIN, AUDIO_VOLUME, PLAY_SONGS
from config import LED_RED_PIN, LED_GREEN_PIN, LED_YELLOW_PIN, ANIMATE_LEDS
from config import PIXELS_PIN, ANIMATE_PIXELS, PIXELS_BRIGHTNESS
from config import SLEEP_INTERVAL, DEMO_MODE

from leds import LED
from music import AudioPin, SongSequence
from neopixel import NeoPixel

audio: AudioPin
music: SongSequence = None

red: LED
green: LED
yellow: LED

red_animation: Animation = None
green_animation: Animation = None
yellow_animation: Animation = None

pixels: NeoPixel
animation: Animation = None


def run(init):
    global audio, music
    global red, green, yellow
    global red_animation, green_animation, yellow_animation
    global pixels, animation

    def button_event():
        if music:
            if music.paused:
                music.resume()
            else:
                music.pause()

    btn_event = button_event

    async def button_loop():
        pin = digitalio.DigitalInOut(BUTTON_PIN)
        pin.direction = digitalio.Direction.INPUT
        pin.pull = digitalio.Pull.UP
        switch = Debouncer(pin)
        while btn_event:
            await asyncio.sleep(SLEEP_INTERVAL / 1000)
            switch.update()
            if switch.rose:
                btn_event()

    async def animate_leds():
        while True:
            if ANIMATE_LEDS:
                if red_animation:
                    red_animation.animate()
                if green_animation:
                    green_animation.animate()
                if yellow_animation:
                    yellow_animation.animate()

                await asyncio.sleep(SLEEP_INTERVAL / 1000)
            else:
                await asyncio.sleep(1)

    async def animate_pixels():
        while True:
            if ANIMATE_PIXELS:
                if animation:
                    animation.animate()
                await asyncio.sleep(SLEEP_INTERVAL / 1000)
            else:
                await asyncio.sleep(1)

    async def play_songs():
        while True:
            if PLAY_SONGS:
                if music:
                    music.play()
                await asyncio.sleep(SLEEP_INTERVAL / 1000)
            else:
                await asyncio.sleep(1)

    async def execute():
        led_task = asyncio.create_task(animate_leds())
        music_task = asyncio.create_task(play_songs())
        pixels_task = asyncio.create_task(animate_pixels())
        button_task = asyncio.create_task(button_loop())

        await asyncio.gather(led_task, music_task, pixels_task, button_task)

    audio = AudioPin(AUDIO_PIN, int(AUDIO_VOLUME * (2 ** 10)))

    red = LED(LED_RED_PIN, 0)
    green = LED(LED_GREEN_PIN, 0)
    yellow = LED(LED_YELLOW_PIN, 0)

    pixels = NeoPixel(PIXELS_PIN, 8, brightness=PIXELS_BRIGHTNESS, auto_write=False)
    pixels.fill(BLACK)
    pixels.write()

    if DEMO_MODE:
        demo.init(audio, red, green, yellow, pixels)
    else:
        init(audio, red, green, yellow, pixels)

    asyncio.run(execute())
