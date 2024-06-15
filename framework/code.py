# Sample basic application showing how to setup and use the pico-interactive framework.
import runner

if __name__ == '__main__':
    i: int = 0


    # Allow the callback to run 10 times before terminating.
    async def callback() -> None:
        global i
        i += 1
        runner.cancel = i == 10


    runner.run(callback)
