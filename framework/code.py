# Sample basic application showing how to setup and use the pico-interactive framework.
import environment
import runner
from framework.button import ButtonController
from framework.polyfills.button import new_button

BUTTON_PIN = " "

if environment.are_pins_available():
    import board

    BUTTON_PIN = board.GP27

if __name__ == '__main__':
    i: int = 0


    async def callback() -> None:
        global i
        i += 1
        runner.cancel = i == 30


    runner = runner.Runner()

    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.register(runner)

    runner.run(callback)
