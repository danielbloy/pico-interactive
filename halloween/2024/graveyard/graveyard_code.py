# NOTE: Rename this to code.py on the graveyard node.
import asyncio
from random import randint, uniform

from interactive.audio import AudioController
from interactive.button import ButtonController
from interactive.configuration import BUTTON_PIN, TRIGGER_DURATION, AUDIO_PIN
from interactive.configuration import LIGHTNING_MIN_BRIGHTNESS, LIGHTNING_MAX_BRIGHTNESS
from interactive.configuration import LIGHTNING_MIN_FLASHES, LIGHTNING_MAX_FLASHES
from interactive.configuration import SPIDER_PINS, SPIDER_COLOURS, SPIDER_PERIODS
from interactive.configuration import TRIGGER_PIN, LIGHTNING_PIN
from interactive.environment import is_running_on_desktop
from interactive.log import info
from interactive.memory import setup_memory_reporting
from interactive.polyfills.animation import BLACK, Pulse, WHITE
from interactive.polyfills.audio import new_mp3_player
from interactive.polyfills.button import new_button
from interactive.polyfills.pixel import new_pixels
from interactive.runner import Runner
from interactive.scheduler import new_triggered_task, TriggerTimedEvents, Triggerable, new_one_time_on_off_task

# collections.abc is not available in CircuitPython.
if is_running_on_desktop():
    pass

PIXELS_OFF = 0.0

SPIDER_PIXELS = 4
SPIDER_BRIGHTNESS = 1.0
SPIDER_SPEED = 0.1

# Because of memory constraints when using a Pico W CircuitPython image we do not use the
# Interactive class here. This allows for much easier testing but also keeps the code
# consistent with network_code.py which must use the Pico W CircuitPython image.
# Doing the setup ourselves saves a notable amount of RAM.
runner = Runner()

runner.cancel_on_exception = False
runner.restart_on_exception = True
runner.restart_on_completion = False

spiders = [new_pixels(pin, SPIDER_PIXELS, brightness=SPIDER_BRIGHTNESS) for pin in SPIDER_PINS if pin is not None]
animations = [Pulse(pixel, speed=SPIDER_SPEED, color=SPIDER_COLOURS[idx], period=SPIDER_PERIODS[idx]) for idx, pixel in
              enumerate(spiders)]

audio_controller = AudioController(new_mp3_player(AUDIO_PIN, "interactive/mp3.mp3"))
audio_controller.register(runner)

# We support multiple different thunder sounds.
thunder = [
    "thunder_3a.mp3",
    "thunder_3b.mp3",
    "thunder_3c.mp3",
    "thunder_2.mp3",
]

# The event is the skull index to enable
trigger_events = TriggerTimedEvents()
trigger_events.add_event(00.00, 99)  # Trigger lightning
trigger_events.add_event(01.00, 0)  # Trigger thunder
trigger_events.add_event(9.00, 99)  # Trigger lightning
trigger_events.add_event(10.00, 1)  # Trigger thunder
trigger_events.add_event(20.00, 99)  # Trigger lightning
trigger_events.add_event(21.00, 2)  # Trigger thunder
trigger_events.add_event(30.00, 99)  # Trigger lightning
trigger_events.add_event(31.00, 3)  # Trigger thunder

# Inspiration for lightning taken from these online articles:
# https://randommakingencounters.com/lightning-and-thunder-effect-arduino-dfplayer-mini-neopixels/
# https://www.tweaking4all.com/forum/arduino/lightning-effect/

# Each time we trigger a lightning strike, we generate the following information:
# * How many flashes to generate within a min and max range.
# * For each flash we generate:
#   * The length of each flash within a min and max range.
#   * The time between each flash within a min and max range.
#
# Each time the pixels are turned on, we also generate:
# * The brightness of the flash within a min and max range.
#
lightning = new_pixels(LIGHTNING_PIN, 24, brightness=PIXELS_OFF)


async def lightning_on() -> None:
    lightning.fill(WHITE)
    lightning.brightness = uniform(LIGHTNING_MIN_BRIGHTNESS, LIGHTNING_MAX_BRIGHTNESS)
    lightning.show()


async def lightning_off() -> None:
    lightning.fill(BLACK)
    lightning.brightness = PIXELS_OFF
    lightning.show()


async def lightning_finish() -> None:
    await lightning_off()


async def lightning_effect() -> None:
    info("Running lightning effect")
    lightning_task = new_one_time_on_off_task(
        cycles=randint(LIGHTNING_MIN_FLASHES, LIGHTNING_MAX_FLASHES),
        on_duration_func=lambda: randint(5, 75) / 1000,  # ms
        off_duration_func=lambda: randint(35, 75) / 1000,  # ms
        on=lightning_on,
        off=lightning_off,
        finish=lightning_finish
    )
    await lightning_task()


async def start_display() -> None:
    for spider in spiders:
        spider.brightness = SPIDER_BRIGHTNESS
        spider.show()

    lightning.fill(BLACK)
    lightning.brightness = PIXELS_OFF
    lightning.show()

    trigger_events.start()


async def run_display() -> None:
    events = trigger_events.run()

    for event in events:
        if event.event < 10:  # Trigger thunder
            audio_controller.queue(thunder[event.event])
        elif event.event == 99:  # Trigger lightning
            # Run the lightning effect in a separate task.
            asyncio.create_task(lightning_effect())

    for animation in animations:
        animation.animate()


async def stop_display() -> None:
    trigger_events.stop()

    for spider in spiders:
        spider.brightness = PIXELS_OFF
        spider.show()

    lightning.fill(BLACK)
    lightning.brightness = PIXELS_OFF
    lightning.show()

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


button_controller = ButtonController(new_button(BUTTON_PIN))
button_controller.add_single_press_handler(button_press)
button_controller.register(runner)

trigger_controller = ButtonController(new_button(TRIGGER_PIN))
trigger_controller.add_single_press_handler(button_press)
trigger_controller.register(runner)

setup_memory_reporting(runner)
runner.run()
