import asyncio
import time

from framework.control import NS_PER_SECOND, SCHEDULER_DEFAULT_FREQUENCY, SCHEDULER_INTERNAL_LOOP_RATIO
from framework.environment import is_running_on_desktop
from framework.log import debug

# collections.abc is not available in CircuitPython.
if is_running_on_desktop():
    from collections.abc import Callable, Awaitable


def never_terminate() -> bool:
    """
    Always returns false so the scheduled task never terminates.
    """
    return False


def terminate_on_cancel(cancellable) -> Callable[[], bool]:
    """
    Returns a function that will terminate the scheduled task based on
    whether the provided cancellable "thing" has been cancelled or not.
    This is detected through testing for a cancel property on cancellable.

    :param cancellable: The thing to use to terminate the scheduled task.
    """

    def cancel_func() -> bool:
        return cancellable.cancel

    return cancel_func


def new_scheduled_task(
        task: Callable[[], Awaitable[None]],
        cancel_func: Callable[[], bool] = never_terminate,
        frequency: int = SCHEDULER_DEFAULT_FREQUENCY) -> Callable[[], Awaitable[None]]:
    """
    Returns an async task function that will invoke the provided task at the
    desired frequency until the cancel_func returns True. The returned task can
    be added to a Runner so it is called regularly in the background.

    :param task: This is called once every cycle based on the callback frequency.
    :param frequency: The desired frequency to invoke the task.
    :param cancel_func: A function that returns whether to cancel the task or not.
    """

    interval = 1 / frequency
    interval_ns: int = int(interval * NS_PER_SECOND)
    next_callback_ns = time.monotonic_ns()

    sleep_interval = interval / SCHEDULER_INTERNAL_LOOP_RATIO

    async def handler() -> None:
        nonlocal interval_ns, next_callback_ns, sleep_interval
        while not cancel_func():
            if time.monotonic_ns() >= next_callback_ns:
                next_callback_ns += interval_ns
                debug(f'Calling scheduled task {task}')
                await task()

            await asyncio.sleep(sleep_interval)

    return handler
