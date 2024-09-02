import asyncio
import time

from interactive.control import (NS_PER_SECOND, ASYNC_LOOP_SLEEP_INTERVAL,
                                 SCHEDULER_DEFAULT_FREQUENCY, SCHEDULER_INTERNAL_LOOP_RATIO)
from interactive.environment import is_running_on_desktop
from interactive.log import debug

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


def new_loop_task(
        task: Callable[[], Awaitable[None]],
        cancel_func: Callable[[], bool] = never_terminate) -> Callable[[], Awaitable[None]]:
    """
    Returns an async task that just loops until the cancel_func returns True. This
    helps avoid having to write the same loop code endlessly.

    :param task: This is called once every cycle.
    :param cancel_func: A function that returns whether to cancel the task or not.
    """

    async def handler() -> None:
        while not cancel_func():
            await asyncio.sleep(ASYNC_LOOP_SLEEP_INTERVAL)
            await task()

    return handler


class Triggerable:
    """Trivial implementation for a triggerable object."""

    def __init__(self):
        self.triggered = False


class TriggerableAlwaysOn:
    """Trivial implementation for a triggerable object that is always triggered."""

    @property
    def triggered(self):
        return True

    @triggered.setter
    def triggered(self, value):
        pass


def new_triggered_task(
        triggerable,
        duration: float,
        start: Callable[[], Awaitable[None]] = None,
        run: Callable[[], Awaitable[None]] = None,
        stop: Callable[[], Awaitable[None]] = None,
        cancel_func: Callable[[], bool] = never_terminate) -> Callable[[], Awaitable[None]]:
    """
    Returns an async task that will only invoke the functions start, stop and run if the
    trigger has been activated. The start function will be called once when the trigger
    is activated, run will be called as a normal loop task whilst the trigger is activated
    and stop will be called once when the trigger is deactivated; which will occurs as the
    specified number of seconds after the trigger has been activated.

    At least one of start, stop and run must be provided, but they need not all be specified.

    Once a trigger is activated, it will not be activated again until after it has expired
    and been deactivated. The triggerable object is used to activate the trigger via a
    "triggered" property.

    The returned task can be added to a Runner so it is called when triggered. The returned
    callback is itself wrapped in a loop_task so can be added to the Runner with add_task().

    :param triggerable: Object that has a triggered property which will activate.
    :param duration: The duration that trigger lasts (i.e. the time between start and stop calls).
    :param start: This is called once when the trigger is activated
    :param run: This is called once every cycle when triggered.
    :param stop: This is called once when the trigger expires.
    :param cancel_func: A function that returns whether to cancel the task or not.
    """

    if start is None and run is None and stop is None:
        raise ValueError("at least one of start, run or stop must be specified")

    running = False
    stop_time = 0

    async def handler() -> None:
        nonlocal running, stop_time

        now = time.monotonic()

        if triggerable.triggered and not running:
            debug("Start running trigger event")
            stop_time = now + duration
            running = True
            if start is not None:
                await start()

        triggerable.triggered = False

        if running and now >= stop_time:
            debug("Stop running trigger event")
            running = False
            if stop is not None:
                await stop()

        if running and run is not None:
            debug("Sunning trigger event")
            await run()

    return new_loop_task(handler, cancel_func)


class TriggerTimedEvents:
    """
    This class is used to trigger events that need to happen at specified times after the
    trigger is started. There is no way to pause a TriggerTimedEvents once it is triggered,
    though it can be stopped/reset.

    Events that are triggered are returned by the run() function. This does a simple check
    to see how much time has elapsed since the trigger was started and return all Events
    that have elapsed. Events are only triggered once during a "run" of the tigger.

    Multiple different events can be added for the same time and will all be fired; though
    the order those events are returned from run() is not guaranteed.

    A TriggerTimedEvents can be used in conjunction with a new_triggered_task() to generate
    the events based on an initial trigger event.
    """

    class Event:
        def __init__(self, trigger_time: float, event: int):
            self.trigger_time = trigger_time
            self.event = event

    def __init__(self):
        self.__running = False
        self.__start_time = 0
        self.__events_remaining = None
        self.events = []

    def start(self):
        if self.__running:
            return

        self.__start_time = time.monotonic()
        self.__running = True
        self.__events_remaining = self.events.copy()

    def stop(self):
        if not self.__running:
            return

        self.__start_time = 0
        self.__running = False
        del self.__events_remaining

    def reset(self):
        self.stop()

    @property
    def running(self):
        return self.__running

    def run(self) -> [Event]:
        if not self.running:
            return

        # If all events have been exhausted then stop running
        if self.__events_remaining is None or len(self.__events_remaining) <= 0:
            self.stop()
            return

        # Get all items that need to be fired.
        now = time.monotonic()
        diff = now - self.__start_time
        events_to_fire = [event for event in self.__events_remaining if diff >= event.trigger_time]

        # Remove those that have been fired
        for event in events_to_fire:
            self.__events_remaining.remove(event)

        return events_to_fire

    def add_event(self, trigger_time: float, event: int):
        self.events.append(self.Event(trigger_time, event))
