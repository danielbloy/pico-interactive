import asyncio

from framework.runner import Runner

if __name__ == '__main__':
    i: int = 0


    # Allow the callback to run 10 times before terminating.
    async def callback() -> None:
        global i
        i += 1
        print(f'i={i}')
        runner.cancel = i == 30


    # Runs forever.
    async def task1():
        while True:
            print("task1")
            await asyncio.sleep(2.0)


    # Ends
    async def task2():
        print("task2")
        await asyncio.sleep(0.005)


    # Throws an exception
    async def task3():
        print("task3")
        await asyncio.sleep(0.005)
        raise Exception("Raised by task 3")


    runner = Runner()
    runner.restart_on_completion = True
    runner.restart_on_exception = True
    runner.cancel_on_exception = False
    runner.add_task(task1)
    runner.add_task(task2)
    runner.add_task(task3)
    runner.run(callback)
