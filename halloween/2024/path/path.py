import gc

from interactive.animation import Flicker
from interactive.audio import AudioController
from interactive.button import ButtonController
from interactive.configuration import get_node_config
from interactive.memory import report_memory_usage, report_memory_usage_and_free
from interactive.polyfills.animation import BLACK, ORANGE
from interactive.polyfills.audio import new_mp3_player
from interactive.polyfills.button import new_button
from interactive.polyfills.pixel import new_pixels
from interactive.runner import Runner
from interactive.scheduler import new_triggered_task, TriggerableAlwaysOn, TriggerTimedEvents, Triggerable

SKULL_BRIGHTNESS = 1.0
SKULL_OFF = 0.0
SKULL_SPEED = 0.1
SKULL_COLOUR = ORANGE


# Because of memory constraints, we do not use the Interactive class here.
# Rather, we setup everything ourselves to minimise what we pull in.
def run_path(skull_pins: list, primary: bool):
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
        triggerable.triggered = True

    async def start_display() -> None:
        for pixel in pixels:
            pixel.fill(BLACK)
            pixel.brightness = SKULL_OFF
            pixel.show()

        if primary:
            audio_controller.queue("bells.mp3")
        else:
            # TODO: Add in a delay for the lion.
            audio_controller.queue("lion.mp3")

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

        for pixel in pixels:
            pixel.fill(BLACK)
            pixel.brightness = SKULL_OFF
            pixel.show()

    config = get_node_config()

    runner = Runner()

    runner.cancel_on_exception = False
    runner.restart_on_exception = True
    runner.restart_on_completion = False

    button_controller = ButtonController(new_button(config.button_pin))
    button_controller.add_single_press_handler(trigger_display)
    button_controller.register(runner)

    audio_controller = AudioController(new_mp3_player(config.audio_pin, "interactive/mp3.mp3"))
    audio_controller.register(runner)

    triggerable = Triggerable()
    trigger_loop = new_triggered_task(
        triggerable,
        duration=config.trigger_duration,
        start=start_display,
        run=run_display,
        stop=stop_display)
    runner.add_task(trigger_loop)

    if config.report_ram:
        async def report_memory() -> None:
            report_memory_usage("report_memory()")

        report_memory_task = (
            new_triggered_task(
                TriggerableAlwaysOn(), config.report_ram_period, start=report_memory))
        runner.add_task(report_memory_task)

    if config.garbage_collect:
        async def garbage_collect() -> None:
            report_memory_usage_and_free("garbage_collect()")

        garbage_collect_task = (
            new_triggered_task(
                TriggerableAlwaysOn(), config.garbage_collect_period, stop=garbage_collect))
        runner.add_task(garbage_collect_task)

    if config.report_ram:
        report_memory_usage('Before execution')

    del config
    gc.collect()

    async def callback() -> None:
        if runner.cancel:
            await stop_display()

    runner.run(callback)
