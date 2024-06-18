import asyncio

from framework.runner import Runner

if __name__ == '__main__':
    i: int = 0


    async def callback() -> None:
        global i
        i += 1
        print(f'i={i}')
        runner.cancel = i == 30


    async def runs_forever_task():
        while True:
            print("task1")
            await asyncio.sleep(2.0)


    async def completes_task():
        print("task2")
        await asyncio.sleep(0.005)


    async def raises_exception_task():
        print("task3")
        await asyncio.sleep(0.005)
        raise Exception("Raised by task 3")


    runner = Runner()
    runner.restart_on_completion = True
    runner.restart_on_exception = True
    runner.cancel_on_exception = False
    runner.add_task(runs_forever_task)
    runner.add_task(completes_task)
    runner.add_task(raises_exception_task)
    runner.run(callback)
