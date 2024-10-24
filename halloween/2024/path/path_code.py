# NOTE: Rename this to code.py on each path microcontroller (primary and secondary).

from interactive.animation import Flicker
from interactive.audio import AudioController
from interactive.button import ButtonController
from interactive.configuration import AUDIO_PIN, BUTTON_PIN, TRIGGER_DURATION
from interactive.configuration import SKULL_PINS, PRIMARY_NODE, TRIGGER_PIN
from interactive.memory import setup_memory_reporting
from interactive.polyfills.animation import BLACK, ORANGE
from interactive.polyfills.audio import new_mp3_player
from interactive.polyfills.button import new_button
from interactive.polyfills.pixel import new_pixels
from interactive.runner import Runner
from interactive.scheduler import new_triggered_task, TriggerTimedEvents, Triggerable

SKULL_BRIGHTNESS = 1.0
SKULL_OFF = 0.0
SKULL_SPEED = 0.1
SKULL_COLOUR = ORANGE

# Because of memory constraints when using a Pico W CircuitPython image we do not use the
# Interactive class here. This allows for much easier testing but also keeps the code
# consistent with network_code.py which must use the Pico W CircuitPython image.
# Doing the setup ourselves saves a notable amount of RAM.
runner = Runner()

runner.cancel_on_exception = False
runner.restart_on_exception = True
runner.restart_on_completion = False

pixels = [new_pixels(pin, 8, brightness=SKULL_BRIGHTNESS) for pin in SKULL_PINS if pin is not None]
animations = [Flicker(pixel, speed=SKULL_SPEED, color=SKULL_COLOUR) for pixel in pixels]

audio_controller = AudioController(new_mp3_player(AUDIO_PIN, "interactive/mp3.mp3"))
audio_controller.register(runner)

# The event is the skull index to enable
trigger_events = TriggerTimedEvents()
trigger_events.add_event(00.40, 0)  # turn on the lights in time to the bells.
trigger_events.add_event(02.70, 1)
trigger_events.add_event(03.50, 21)  # Lion on secondary
trigger_events.add_event(05.00, 2)
trigger_events.add_event(07.30, 3)
trigger_events.add_event(09.60, 4)
trigger_events.add_event(11.90, 5)
trigger_events.add_event(20.00, 22)  # Dragon on secondary
trigger_events.add_event(28.00, 11)  # Lion on primary
trigger_events.add_event(29.00, 105)  # Turn off the lights
trigger_events.add_event(31.00, 104)
trigger_events.add_event(33.00, 103)
trigger_events.add_event(34.00, 22)  # Dragon on secondary
trigger_events.add_event(35.00, 102)
trigger_events.add_event(37.00, 101)
trigger_events.add_event(39.00, 100)


async def start_display() -> None:
    for pixel in pixels:
        pixel.fill(BLACK)
        pixel.brightness = SKULL_OFF
        pixel.show()

    if PRIMARY_NODE:
        audio_controller.queue("bells.mp3")

    trigger_events.start()


async def run_display() -> None:
    events = trigger_events.run()

    for event in events:
        # turn on the pixels
        if event.event <= 5:
            pixels[event.event].fill(SKULL_COLOUR)
            pixels[event.event].brightness = SKULL_BRIGHTNESS
            pixels[event.event].show()

        # Turn off the pixels
        elif event.event >= 100:
            pixels[event.event - 100].fill(BLACK)
            pixels[event.event - 100].brightness = SKULL_OFF
            pixels[event.event - 100].show()

        elif event.event == 11:
            if PRIMARY_NODE:
                audio_controller.queue("lion.mp3")

        elif event.event == 21:
            if not PRIMARY_NODE:
                audio_controller.queue("lion.mp3")

        elif event.event == 22:
            if not PRIMARY_NODE:
                audio_controller.queue("dragon.mp3")

    for animation in animations:
        animation.animate()


async def stop_display() -> None:
    trigger_events.stop()

    for pixel in pixels:
        pixel.fill(BLACK)
        pixel.brightness = SKULL_OFF
        pixel.show()

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
