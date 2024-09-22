from interactive.animation import Flicker
from interactive.audio import AudioController
from interactive.polyfills.animation import BLACK, ORANGE
from interactive.polyfills.pixel import new_pixels
from interactive.scheduler import TriggerTimedEvents

SKULL_BRIGHTNESS = 1.0
SKULL_OFF = 0.0
SKULL_SPEED = 0.1
SKULL_COLOUR = ORANGE


class PathController:
    def __init__(self, pins: list, audio_controller: AudioController):
        self._audio_controller = audio_controller
        self.pixels = [new_pixels(pin, 8, brightness=SKULL_BRIGHTNESS) for pin in pins if pin is not None]
        self.animations = [Flicker(pixel, speed=SKULL_SPEED, color=SKULL_COLOUR) for pixel in self.pixels]

        self.trigger_events = TriggerTimedEvents()
        # The event is the index to enable
        self.trigger_events.add_event(0.0, 0)
        self.trigger_events.add_event(0.5, 1)
        self.trigger_events.add_event(1.0, 2)
        self.trigger_events.add_event(1.5, 3)
        self.trigger_events.add_event(2.0, 4)
        self.trigger_events.add_event(2.5, 5)

    async def start_display(self) -> None:

        for pixel in self.pixels:
            pixel.fill(BLACK)
            pixel.brightness = SKULL_OFF
            pixel.show()

        self._audio_controller.queue("lion.mp3")

        self.trigger_events.start()

    async def run_display(self) -> None:
        events = self.trigger_events.run()

        for event in events:
            self.pixels[event.event].fill(SKULL_COLOUR)
            self.pixels[event.event].brightness = SKULL_BRIGHTNESS
            self.pixels[event.event].show()

        for animation in self.animations:
            animation.animate()

    async def stop_display(self) -> None:
        self.trigger_events.stop()

        for animation in self.animations:
            animation.freeze()

        for pixel in self.pixels:
            pixel.fill(BLACK)
            pixel.brightness = SKULL_OFF
            pixel.show()
