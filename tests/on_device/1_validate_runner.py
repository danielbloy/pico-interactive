import asyncio

from framework.runner import Runner

if __name__ == '__main__':
    i: int = 0


    # Allow the callback to run 10 times before terminating.
    async def callback() -> None:
        global i
        i += 1
        print(f'i={i}')
        runner.cancel = i == 10


    async def task1():
        print("task1")
        await asyncio.sleep(0.001)


    async def task2():
        print(task2)
        await asyncio.sleep(0.005)


    runner = Runner()
    runner.add_task(task1)
    runner.add_task(task2)
    runner.run(callback)
