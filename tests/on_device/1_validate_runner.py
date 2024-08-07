import asyncio

from interactive.environment import are_pins_available
from interactive.log import set_log_level, debug, info, INFO
from interactive.memory import report_memory_usage_and_free
from interactive.runner import Runner

REPORT_RAM = are_pins_available()

if __name__ == '__main__':
    
    set_log_level(INFO)

    if REPORT_RAM:
        report_memory_usage_and_free("Before creating Objects")


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

    i: int = 0


    async def callback() -> None:
        global i
        i += 1
        debug(f'Callback: i={i}')
        runner.cancel = i == 30


    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    runner.run(callback)

    if REPORT_RAM:
        report_memory_usage_and_free("After running Runner")
