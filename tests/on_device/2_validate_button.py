import asyncio

from framework.button import Button
from framework.environment import are_pins_available
from framework.runner import Runner

BUTTON_PIN = " "

if are_pins_available():
    import board

    BUTTON_PIN = board.GP27

if __name__ == '__main__':
    i: int = 0


    async def callback() -> None:
        global i
        i += 1
        print(f'Callback: i={i}')
        runner.cancel = i == 30


    async def runs_forever_task():
        while True:
            print("LOOP: runs_forever_task")
            await asyncio.sleep(2.0)


    async def completes_task():
        print("START: completes_task")
        await asyncio.sleep(0.005)
        print("FINISH: completes_task")


    async def raises_exception_task():
        print("START: raises_exception_task")
        await asyncio.sleep(0.005)
        print("EXCEPTION: raises_exception_task")
        raise Exception("Raised by task 3")


    runner = Runner()
    runner.restart_on_completion = False
    runner.restart_on_exception = False
    runner.cancel_on_exception = False
    runner.add_task(runs_forever_task)
    runner.add_task(completes_task)
    runner.add_task(raises_exception_task)
    button = Button()
    # TODO: add handlers
    button.register(runner)
    runner.run(callback)
