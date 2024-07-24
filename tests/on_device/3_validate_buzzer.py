import time

from interactive.button import ButtonController
from interactive.buzzer import BuzzerController
from interactive.environment import are_pins_available
from interactive.log import set_log_level, INFO
from interactive.melody import Melody, MelodySequence, decode_melody
from interactive.polyfills.button import new_button
from interactive.polyfills.buzzer import new_buzzer
from interactive.runner import Runner

BUTTON_PIN = None
BUZZER_PIN = None

if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    BUTTON_PIN = board.GP27
    BUZZER_PIN = board.GP2

if __name__ == '__main__':

    set_log_level(INFO)

    notes = [
        "C4:1", "D:1", "E:1", "F:1", "G:1", "A:1", "B:1", "C5:1",
        "B4:1", "A:1", "G:1", "F:1", "E:1", "D:1", "C:1"]

    buzzer = new_buzzer(BUZZER_PIN)
    buzzer.volume = 0.1
    melody = MelodySequence(Melody(buzzer, decode_melody(notes), 0.2))
    melody.pause()


    async def play_melody() -> None:
        if not runner.cancel:
            melody.play()


    async def single_click_handler() -> None:
        buzzer_controller.beeps(3)


    async def multi_click_handler() -> None:
        if melody.paused:
            melody.resume()
        else:
            melody.pause()


    async def long_press_handler() -> None:
        melody.reset()


    runner = Runner()

    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_click_handler(single_click_handler)
    button_controller.add_multi_click_handler(multi_click_handler)
    button_controller.add_long_press_handler(long_press_handler)
    button_controller.register(runner)

    buzzer_controller = BuzzerController(buzzer)
    buzzer_controller.register(runner)
    runner.add_loop_task(play_melody)

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + 10


    async def callback() -> None:
        runner.cancel = time.monotonic() > finish
        if runner.cancel:
            buzzer_controller.off()


    runner.run(callback)
