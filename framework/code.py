# Sample basic application showing how to setup and use the pico-interactive framework.
import runner

if __name__ == '__main__':
    i: int = 0


    async def callback() -> None:
        global i
        i += 1
        runner.cancel = i == 10


    runner = runner.Runner()
    runner.run(callback)
