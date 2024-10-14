# NOTE: Rename this to code.py on the graveyard node.
from random import randint, uniform

from interactive.audio import AudioController
from interactive.button import ButtonController
from interactive.configuration import BUTTON_PIN, TRIGGER_DURATION, AUDIO_PIN
from interactive.configuration import SPIDER_PINS, SPIDER_COLOURS, SPIDER_PERIODS
from interactive.configuration import TRIGGER_PIN, LIGHTNING_PIN, LIGHTNING_MIN_BRIGHTNESS, LIGHTNING_MAX_BRIGHTNESS
from interactive.environment import is_running_on_desktop
from interactive.memory import setup_memory_reporting
from interactive.polyfills.animation import BLACK, Pulse, WHITE
from interactive.polyfills.audio import new_mp3_player
from interactive.polyfills.button import new_button
from interactive.polyfills.pixel import new_pixels
from interactive.runner import Runner
from interactive.scheduler import new_triggered_task, TriggerTimedEvents, Triggerable

# collections.abc is not available in CircuitPython.
if is_running_on_desktop():
    from collections.abc import Callable

PIXELS_OFF = 0.0

SPIDER_BRIGHTNESS = 1.0
SPIDER_SPEED = 0.1


# Inspiration for lightning taken from these online articles:
# https://randommakingencounters.com/lightning-and-thunder-effect-arduino-dfplayer-mini-neopixels/
# https://www.tweaking4all.com/forum/arduino/lightning-effect/

# Each time we trigger a lightning strike, we generate the following information:
# * How many flashes to generate within the minx and max range.
# * For each flash we generate:
#   * The length of each flash within the min and max range.
#   * The time between each flash within the min and max range.
#
# The above information is used to generate a TriggerTimedEvents instance which is used to
# turn the lightning pixels on or off. Each time the pixels are turned on, we also generate:
# * The brightness of the flash.
#
def new_lightning_task() -> Callable[[], bool]:
    lightning_events = TriggerTimedEvents()

    # Represents the start of the next flash.
    next_flash = 0
    for i in range(randint(5, 15)):
        flash_duration = randint(5, 75) / 1000  # Milliseconds
        off_duration = randint(5, 75) / 1000  # Milliseconds

        lightning_events.add_event(next_flash, 1)  # On
        lightning_events.add_event(next_flash + flash_duration, 0)  # Off
        next_flash += flash_duration
        next_flash += off_duration

    lightning_events.add_event(next_flash, 2)  # Terminate

    lightning_events.start()

    def task() -> bool:
        nonlocal lightning_events
        stop = False
        events = lightning_events.run()

        for event in events:
            if event.event == 0:  # Lights off
                lightning.fill(BLACK)
                lightning.brightness = PIXELS_OFF
                lightning.show()
            elif event.event == 1:  # Lights one
                lightning.fill(WHITE)
                lightning.brightness = uniform(LIGHTNING_MIN_BRIGHTNESS, LIGHTNING_MAX_BRIGHTNESS)
                lightning.show()
            elif event.event == 2:  # End
                lightning_events.stop()
                del lightning_events
                stop = True

        return stop

    return task


# Because of memory constraints when using a Pico W CircuitPython image we do not use the
# Interactive class here. This allows for much easier testing but also keeps the code
# consistent with network_code.py which must use the Pico W CircuitPython image.
# Doing the setup ourselves saves a notable amount of RAM.
runner = Runner()

runner.cancel_on_exception = False
runner.restart_on_exception = True
runner.restart_on_completion = False

spiders = [new_pixels(pin, 2, brightness=SPIDER_BRIGHTNESS) for pin in SPIDER_PINS if pin is not None]
animations = [Pulse(pixel, speed=SPIDER_SPEED, color=SPIDER_COLOURS[idx], period=SPIDER_PERIODS[idx]) for idx, pixel in
              enumerate(spiders)]

lightning = new_pixels(LIGHTNING_PIN, 24, brightness=LIGHTNING_BRIGHTNESS)
lightning_task: Callable[[], bool] = None

audio_controller = AudioController(new_mp3_player(AUDIO_PIN, "interactive/mp3.mp3"))
audio_controller.register(runner)

# The event is the skull index to enable
trigger_events = TriggerTimedEvents()
trigger_events.add_event(00.00, 0)  # Trigger lightning
trigger_events.add_event(01.00, 1)  # Trigger thunder


async def start_display() -> None:
    for spider in spiders:
        spider.fill(BLACK)
        spider.brightness = PIXELS_OFF
        spider.show()

    lightning.fill(BLACK)
    lightning.brightness = PIXELS_OFF
    lightning.show()

    trigger_events.start()


async def run_display() -> None:
    global lightning_task

    if lightning_task:
        lightning_finished = lightning_task()
        if lightning_finished:
            del lightning_task
            lightning_task = None

    events = trigger_events.run()

    for event in events:
        if event.event == 0:  # Trigger lightning
            lightning_task = new_lightning_task()
        elif event.event == 1:  # Trigger thunder
            # TODO: audio_controller.queue("dragon.mp3")
            pass

    for animation in animations:
        animation.animate()


async def stop_display() -> None:
    trigger_events.stop()

    for spider in spiders:
        spider.fill(BLACK)
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
