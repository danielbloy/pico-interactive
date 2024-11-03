# This module contains utility functions for examining how much RAM the
# system has available whilst it is running.
#

import gc

from interactive.log import critical
from interactive.runner import Runner


def report_memory_usage(msg: str = ""):
    critical(f"MEMORY USAGE: {msg}")
    critical(f"HEAP: Allocated: {gc.mem_alloc()} bytes, Free: {gc.mem_free()} bytes")


def report_memory_usage_and_free(msg: str = ""):
    report_memory_usage(f"{msg} before gc")
    gc.collect()
    report_memory_usage(f"{msg} after gc")


def setup_memory_reporting(runner: Runner):
    from interactive.configuration import REPORT_RAM, REPORT_RAM_PERIOD, GARBAGE_COLLECT, GARBAGE_COLLECT_PERIOD
    from interactive.scheduler import new_triggered_task, TriggerableAlwaysOn

    if REPORT_RAM:
        async def report_memory() -> None:
            report_memory_usage()

        report_memory_task = (
            new_triggered_task(
                TriggerableAlwaysOn(), REPORT_RAM_PERIOD, start=report_memory))
        runner.add_task(report_memory_task)

    if GARBAGE_COLLECT:
        async def garbage_collect() -> None:
            report_memory_usage_and_free()

        garbage_collect_task = (
            new_triggered_task(
                TriggerableAlwaysOn(), GARBAGE_COLLECT_PERIOD, stop=garbage_collect))
        runner.add_task(garbage_collect_task)

    gc.collect()

    if REPORT_RAM:
        report_memory_usage()
