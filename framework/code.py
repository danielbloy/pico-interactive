# Sample basic application showing how to setup and use the pico-interactive framework.
import button
import environment
import runner

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
    button = button.Button(BUTTON_PIN)
    button.register(runner)

    runner.run(callback)
