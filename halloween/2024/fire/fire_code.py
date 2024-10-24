# NOTE: Rename this to code.py on each cauldron microcontroller.

from interactive.animation import Flicker
from interactive.audio import AudioController
from interactive.button import ButtonController
from interactive.configuration import AUDIO_PIN, TRIGGER_DURATION
from interactive.configuration import FIRE_PIN, TRIGGER_PIN
from interactive.memory import setup_memory_reporting
from interactive.polyfills.animation import BLACK, ORANGE
from interactive.polyfills.audio import new_mp3_player
from interactive.polyfills.button import new_button
from interactive.polyfills.pixel import new_pixels
from interactive.runner import Runner
from interactive.scheduler import new_triggered_task, Triggerable

FIRE_BRIGHTNESS = 1.0
FIRE_OFF = 0.0
FIRE_SPEED = 0.1
FIRE_COLOUR = ORANGE

# Because of memory constraints when using a Pico W CircuitPython image we do not use the
# Interactive class here. This allows for much easier testing but also keeps the code
# consistent with network_code.py which must use the Pico W CircuitPython image.
# Doing the setup ourselves saves a notable amount of RAM.
runner = Runner()

runner.cancel_on_exception = False
runner.restart_on_exception = True
runner.restart_on_completion = False

pixels = new_pixels(FIRE_PIN, 30, brightness=FIRE_BRIGHTNESS)
animation = Flicker(pixels, speed=FIRE_SPEED, color=FIRE_COLOUR)

audio_controller = AudioController(new_mp3_player(AUDIO_PIN, "interactive/mp3.mp3"))
audio_controller.register(runner)


async def start_display() -> None:
    pixels.fill(FIRE_COLOUR)
    pixels.brightness = FIRE_BRIGHTNESS
    pixels.show()

    audio_controller.queue("fire-place.mp3")


async def run_display() -> None:
    animation.animate()


async def stop_display() -> None:
    pixels.fill(BLACK)
    pixels.brightness = FIRE_OFF
    pixels.show()

    audio_controller.stop()


triggerable = Triggerable()

trigger_loop = new_triggered_task(
    triggerable,
    duration=TRIGGER_DURATION,
    start=start_display,
    run=run_display,
    stop=stop_display)
runner.add_task(trigger_loop)


async def button_press() -> None:
    triggerable.triggered = True


trigger_controller = ButtonController(new_button(TRIGGER_PIN))
trigger_controller.add_single_press_handler(button_press)
trigger_controller.register(runner)

setup_memory_reporting(runner)
runner.run()
