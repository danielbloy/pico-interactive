import asyncio

from framework.log import set_log_level, debug, info, INFO
from framework.runner import Runner

if __name__ == '__main__':
    i: int = 0

    set_log_level(INFO)


    async def callback() -> None:
        global i
        i += 1
        debug(f'Callback: i={i}')
        runner.cancel = i == 30


    async def runs_forever_task():
        while True:
            info("LOOP: runs_forever_task")
            await asyncio.sleep(2.0)


    async def completes_task():
        info("START: completes_task")
        await asyncio.sleep(0.005)
        info("FINISH: completes_task")


    async def raises_exception_task():
        info("START: raises_exception_task")
        await asyncio.sleep(0.005)
        info("EXCEPTION: raises_exception_task")
        raise Exception("Raised by task 3")


    runner = Runner()
    runner.restart_on_completion = True
    runner.restart_on_exception = True
    runner.cancel_on_exception = False
    runner.add_task(runs_forever_task)
    runner.add_task(completes_task)
    runner.add_task(raises_exception_task)
    runner.run(callback)
