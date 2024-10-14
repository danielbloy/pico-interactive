# NOTE: Rename this to code.py on the graveyard node.

from interactive.audio import AudioController
from interactive.button import ButtonController
from interactive.configuration import AUDIO_PIN, BUTTON_PIN, TRIGGER_DURATION
from interactive.configuration import SPIDER_PINS, SPIDER_COLOURS, SPIDER_PERIODS
from interactive.configuration import TRIGGER_PIN, LIGHTNING_PIN
from interactive.memory import setup_memory_reporting
from interactive.polyfills.animation import BLACK, Pulse
from interactive.polyfills.audio import new_mp3_player
from interactive.polyfills.button import new_button
from interactive.polyfills.pixel import new_pixels
from interactive.runner import Runner
from interactive.scheduler import new_triggered_task, TriggerTimedEvents, Triggerable

PIXELS_OFF = 0.0

SPIDER_BRIGHTNESS = 1.0
SPIDER_SPEED = 0.1

LIGHTNING_BRIGHTNESS = 1.0

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
# TODO: Add lightning animation.animations.append()

audio_controller = AudioController(new_mp3_player(AUDIO_PIN, "interactive/mp3.mp3"))
audio_controller.register(runner)

# The event is the skull index to enable
trigger_events = TriggerTimedEvents()
trigger_events.add_event(00.40, 0)  # turn on the lights in time to the bells.


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
    events = trigger_events.run()

    for event in events:
        # TODO: Trigger lightning and thunder.
        if event.event == 22:
            audio_controller.queue("dragon.mp3")

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
