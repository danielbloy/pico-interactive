from interactive.animation import Flicker
from interactive.configuration import get_node_config
from interactive.framework import Interactive
from interactive.polyfills.animation import BLACK, ORANGE
from interactive.polyfills.pixel import new_pixels
from interactive.scheduler import TriggerTimedEvents

SKULL_BRIGHTNESS = 1.0
SKULL_OFF = 0.0
SKULL_SPEED = 0.1
SKULL_COLOUR = ORANGE


# TODO: need to extract out the audio as only the primary plays audio.
def run_path(skull_pins: list):
    pixels = [new_pixels(pin, 8, brightness=SKULL_BRIGHTNESS) for pin in skull_pins if pin is not None]
    animations = [Flicker(pixel, speed=SKULL_SPEED, color=SKULL_COLOUR) for pixel in pixels]

    trigger_events = TriggerTimedEvents()
    # The event is the index to enable
    trigger_events.add_event(0.0, 0)
    trigger_events.add_event(0.5, 1)
    trigger_events.add_event(1.0, 2)
    trigger_events.add_event(1.5, 3)
    trigger_events.add_event(2.0, 4)
    trigger_events.add_event(2.5, 5)

    async def trigger_display() -> None:
        interactive.triggerable.triggered = True

    async def start_display() -> None:
        for pixel in pixels:
            pixel.fill(BLACK)
            pixel.brightness = SKULL_OFF
            pixel.show()

        interactive.audio_controller.queue("lion.mp3")

        trigger_events.start()

    async def run_display() -> None:
        events = trigger_events.run()

        for event in events:
            pixels[event.event].fill(SKULL_COLOUR)
            pixels[event.event].brightness = SKULL_BRIGHTNESS
            pixels[event.event].show()

        for animation in animations:
            animation.animate()

    async def stop_display() -> None:
        trigger_events.stop()

        for animation in animations:
            animation.freeze()

        for pixel in pixels:
            pixel.fill(BLACK)
            pixel.brightness = SKULL_OFF
            pixel.show()

    config = get_node_config(network=False, button=True, buzzer=False, audio=True, ultrasonic=False, trigger=True)
    config.trigger_start = start_display
    config.trigger_run = run_display
    config.trigger_stop = stop_display
    config.button_single_press = trigger_display

    interactive = Interactive(config)

    del config

    async def callback() -> None:
        if interactive.cancel:
            await stop_display()

    interactive.run(callback)
