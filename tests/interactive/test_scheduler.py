import asyncio
import time

import pytest

from interactive.control import SCHEDULER_DEFAULT_FREQUENCY, ASYNC_LOOP_SLEEP_INTERVAL
from interactive.scheduler import never_terminate, terminate_on_cancel, new_scheduled_task, new_loop_task, \
    new_triggered_task, Triggerable, TriggerableAlwaysOn, TriggerTimedEvents


class Cancellable:
    def __init__(self):
        self.cancel = False


class CancellableCount:
    def __init__(self, count):
        self.left = count

    @property
    def cancel(self):
        self.left -= 1
        return self.left <= 0

    def reset(self, count) -> None:
        self.left = count


class CancellableDuration:
    def __init__(self, seconds):
        self.seconds = seconds
        self.__end = None

    @property
    def cancel(self):
        if self.__end is None:
            self.__end = time.time() + self.seconds

        return time.time() >= self.__end

    def reset(self):
        self.__end = None


class TestScheduler:
    def test_never_terminate(self) -> None:
        """The simplest of all tests"""
        assert not never_terminate()

    def test_terminate_on_cancel(self) -> None:
        """
        Validates that terminate_on_cancel() returns a function whose
        return value when called is the cancel value of the passed in
        object.
        """

        cancellable = Cancellable()

        fn = terminate_on_cancel(cancellable)

        assert not fn()

        cancellable.cancel = True
        assert fn()

        cancellable.cancel = False
        assert not fn()
        assert not fn()

        cancellable.cancel = True
        assert fn()

    def test_triggerable_always_on_always_returns_true(self) -> None:
        """
        Validates that the TriggerableAlwaysOn class always returns True
        for triggered.
        """
        triggerable = TriggerableAlwaysOn()
        assert triggerable.triggered

        triggerable.triggered = True
        assert triggerable.triggered

        triggerable.triggered = False
        assert triggerable.triggered

    def test_task_never_called(self) -> None:
        """
        Validates that the returned task terminates straight away
        when the terminate_func always returns true.
        """

        cancellable = Cancellable()
        cancel_fn = terminate_on_cancel(cancellable)
        cancellable.cancel = True

        called = False

        async def task():
            nonlocal called
            called = True

        scheduled_task = new_scheduled_task(task, cancel_fn)

        # noinspection PyTypeChecker
        asyncio.run(scheduled_task())
        assert not called

        loop_task = new_loop_task(task, cancel_fn)

        # noinspection PyTypeChecker
        asyncio.run(loop_task())
        assert not called

        triggerable = Triggerable()
        trigger_task = new_triggered_task(triggerable, duration=1.0, run=task, cancel_func=cancel_fn)

        # noinspection PyTypeChecker
        asyncio.run(trigger_task())
        assert not called

    def test_task_stops(self) -> None:
        """
        Validates that the returned task terminates
        when the terminate_func returns true.
        """

        cancellable = CancellableCount(2)
        cancel_fn = terminate_on_cancel(cancellable)

        called = 0

        async def task():
            nonlocal called
            called += 1

        scheduled_task = new_scheduled_task(task, cancel_fn)

        # noinspection PyTypeChecker
        asyncio.run(scheduled_task())
        assert called == 1
        assert cancellable.cancel

        loop_task = new_loop_task(task, cancel_fn)

        called = 0
        cancellable.reset(2)

        # noinspection PyTypeChecker
        asyncio.run(loop_task())
        assert called == 1
        assert cancellable.cancel

        triggerable = Triggerable()
        triggerable.triggered = True
        trigger_task = new_triggered_task(triggerable, duration=1.0, run=task, cancel_func=cancel_fn)

        called = 0
        cancellable.reset(2)

        # noinspection PyTypeChecker
        asyncio.run(trigger_task())
        assert called == 1
        assert cancellable.cancel

    def test_task_called_multiple_times(self) -> None:
        """
        Validates that the returned task terminates after having been
        called multiple times. Because of the way the loop works, the
        number of times the callback is called will not be equal to the
        number of times the task is invoked; especially on fast computes.
        """

        cancellable = CancellableCount(20)
        cancel_fn = terminate_on_cancel(cancellable)

        called = 0

        async def task():
            nonlocal called
            called += 1

        scheduled_task = new_scheduled_task(task, cancel_fn)

        # noinspection PyTypeChecker
        asyncio.run(scheduled_task())
        assert called > 2
        assert called <= 20
        assert cancellable.cancel

        loop_task = new_loop_task(task, cancel_fn)

        called = 0
        cancellable.reset(20)

        # noinspection PyTypeChecker
        asyncio.run(loop_task())
        assert called > 2
        assert called <= 20
        assert cancellable.cancel

        triggerable = Triggerable()
        triggerable.triggered = True
        trigger_task = new_triggered_task(triggerable, duration=1.0, run=task, cancel_func=cancel_fn)

        called = 0
        cancellable.reset(20)

        # noinspection PyTypeChecker
        asyncio.run(trigger_task())
        assert called > 2
        assert called <= 20
        assert cancellable.cancel

    def test_run_invokes_scheduled_task_callback_with_sensible_frequency(self) -> None:
        """
        This test allows the callback to be called the same number of times
        as the default callback frequency and validates that we are within
        a tolerance of 5%. At the same time, a busy blocking background task
        is running which prevents the dumb method of sleeping from working.
        """
        called_count: int = 0
        seconds_to_run: int = 2

        async def task():
            nonlocal called_count
            called_count += 1
            await asyncio.sleep(ASYNC_LOOP_SLEEP_INTERVAL)

        cancellable = CancellableDuration(seconds_to_run)
        cancel_fn = terminate_on_cancel(cancellable)

        scheduled_task = new_scheduled_task(task, cancel_fn)

        start = time.time()
        # noinspection PyTypeChecker
        asyncio.run(scheduled_task())
        end = time.time()

        assert (end - start) < (seconds_to_run * 1.05)
        assert (end - start) > (seconds_to_run * 0.95)
        expected_called_count = seconds_to_run * SCHEDULER_DEFAULT_FREQUENCY
        assert called_count >= expected_called_count - 1
        assert called_count <= expected_called_count + 1

    def test_run_invokes_scheduled_task_callback_with_custom_frequency(self) -> None:
        """
        This test is the same as test_scheduled_task_invokes_callback_with_sensible_frequency()
        but we specify a custom frequency instead.
        """
        called_count: int = 0
        seconds_to_run: int = 2
        frequency: int = 10

        async def task():
            nonlocal called_count
            called_count += 1
            await asyncio.sleep(ASYNC_LOOP_SLEEP_INTERVAL)

        cancellable = CancellableDuration(seconds_to_run)
        cancel_fn = terminate_on_cancel(cancellable)

        scheduled_task = new_scheduled_task(task, cancel_fn, frequency)

        start = time.time()
        # noinspection PyTypeChecker
        asyncio.run(scheduled_task())
        end = time.time()

        assert (end - start) < (seconds_to_run * 1.05)
        assert (end - start) > (seconds_to_run * 0.95)
        expected_called_count = seconds_to_run * frequency
        assert called_count >= expected_called_count - 1
        assert called_count <= expected_called_count + 1

    def test_run_invokes_loop_task_callback_with_custom_frequency(self) -> None:
        """
        This test is similar to the scheduled_task frequency tests above but the
        loop task will execute many more times.
        """
        called_count: int = 0
        seconds_to_run: int = 2

        async def task():
            nonlocal called_count
            called_count += 1

        cancellable = CancellableDuration(seconds_to_run)
        cancel_fn = terminate_on_cancel(cancellable)

        loop_task = new_loop_task(task, cancel_fn)

        start = time.time()
        # noinspection PyTypeChecker
        asyncio.run(loop_task())
        end = time.time()

        assert (end - start) < (seconds_to_run * 1.05)
        assert (end - start) > (seconds_to_run * 0.95)
        assert called_count >= 50

    def test_run_invokes_triggered_task_callback_with_sensible_frequency(self) -> None:
        """
        Same as test_run_invokes_loop_task_callback_with_custom_frequency() but
        for the run callback of a triggered_task.
        """
        called_count: int = 0
        seconds_to_run: int = 2

        async def task():
            nonlocal called_count
            called_count += 1
            await asyncio.sleep(ASYNC_LOOP_SLEEP_INTERVAL)

        cancellable = CancellableDuration(seconds_to_run)
        cancel_fn = terminate_on_cancel(cancellable)

        triggerable = Triggerable()
        triggerable.triggered = True
        trigger_task = new_triggered_task(triggerable, duration=seconds_to_run, run=task, cancel_func=cancel_fn)

        start = time.time()
        # noinspection PyTypeChecker
        asyncio.run(trigger_task())
        end = time.time()

        assert (end - start) < (seconds_to_run * 1.05)
        assert (end - start) > (seconds_to_run * 0.95)
        assert called_count >= 50

    def test_triggered_task_errors_with_no_callback(self) -> None:
        """
        Validates an error is raised when new_triggered_task() is invoked
        without a start, stop or run.
        """
        triggerable = Triggerable()
        with pytest.raises(ValueError):
            # noinspection PyTypeChecker
            new_triggered_task(triggerable, duration=0.1)

    def test_triggered_task_invokes_start_callback(self) -> None:
        """
        Validates that the start callback is called when the task is triggered.
        """
        called_count: int = 0
        seconds_to_run: int = 2

        async def task():
            nonlocal called_count
            called_count += 1
            await asyncio.sleep(ASYNC_LOOP_SLEEP_INTERVAL)

        cancellable = CancellableDuration(seconds_to_run)
        cancel_fn = terminate_on_cancel(cancellable)

        triggerable = Triggerable()
        triggerable.triggered = True
        trigger_task = new_triggered_task(triggerable, duration=1.0, start=task, cancel_func=cancel_fn)

        # noinspection PyTypeChecker
        asyncio.run(trigger_task())

        assert called_count == 1

    def test_triggered_task_invokes_run_callback(self) -> None:
        """
        Validates that the run callback is called repeatedly when the task is triggered.
        """
        called_count: int = 0
        seconds_to_run: int = 2

        async def task():
            nonlocal called_count
            called_count += 1
            await asyncio.sleep(ASYNC_LOOP_SLEEP_INTERVAL)

        cancellable = CancellableDuration(seconds_to_run)
        cancel_fn = terminate_on_cancel(cancellable)

        triggerable = Triggerable()
        triggerable.triggered = True
        trigger_task = new_triggered_task(triggerable, duration=1.0, run=task, cancel_func=cancel_fn)

        # noinspection PyTypeChecker
        asyncio.run(trigger_task())

        assert called_count >= SCHEDULER_DEFAULT_FREQUENCY

    def test_triggered_task_invokes_stop_callback(self) -> None:
        """
        Validates that the stop callback is called when the triggered task expires.
        """
        called_count: int = 0
        seconds_to_run: int = 2

        async def task():
            nonlocal called_count
            called_count += 1
            await asyncio.sleep(ASYNC_LOOP_SLEEP_INTERVAL)

        cancellable = CancellableDuration(seconds_to_run)
        cancel_fn = terminate_on_cancel(cancellable)

        triggerable = Triggerable()
        triggerable.triggered = True
        trigger_task = new_triggered_task(triggerable, duration=1.0, stop=task, cancel_func=cancel_fn)

        # noinspection PyTypeChecker
        asyncio.run(trigger_task())

        assert called_count == 1

    def test_triggered_task_callbacks_invoked_in_correct_order(self) -> None:
        """
        Validates that the start, run and stop callbacks are called in the correct
        order when the task is triggered.
        """
        seconds_to_run: int = 2

        start_time = 0
        stop_time = 0
        run_start_time = -1
        run_stop_time = 0

        async def start():
            nonlocal start_time
            start_time = time.time()
            await asyncio.sleep(ASYNC_LOOP_SLEEP_INTERVAL)

        async def run():
            nonlocal run_start_time, run_stop_time
            await asyncio.sleep(ASYNC_LOOP_SLEEP_INTERVAL)
            if run_start_time < 0:
                run_start_time = time.time()
            run_stop_time = time.time()

        async def stop():
            nonlocal stop_time
            stop_time = time.time()
            await asyncio.sleep(ASYNC_LOOP_SLEEP_INTERVAL)

        cancellable = CancellableDuration(seconds_to_run)
        cancel_fn = terminate_on_cancel(cancellable)

        triggerable = Triggerable()
        triggerable.triggered = True
        trigger_task = new_triggered_task(triggerable, duration=1.0, start=start, run=run, stop=stop,
                                          cancel_func=cancel_fn)

        # noinspection PyTypeChecker
        asyncio.run(trigger_task())

        assert start_time < run_start_time
        assert run_start_time < run_stop_time
        assert run_stop_time < stop_time

    def test_triggered_tasks_do_not_overlap(self) -> None:
        """
        Validates that a second triggered task does not get invoked when it has
        already been triggered and is still running.
        """
        seconds_to_run: int = 2

        start_count = 0
        stop_count = 0

        async def start():
            nonlocal start_count
            start_count += 1
            await asyncio.sleep(ASYNC_LOOP_SLEEP_INTERVAL)

        async def run():
            triggerable.triggered = True
            await asyncio.sleep(ASYNC_LOOP_SLEEP_INTERVAL)

        async def stop():
            nonlocal stop_count
            stop_count += 1
            await asyncio.sleep(ASYNC_LOOP_SLEEP_INTERVAL)

        cancellable = CancellableDuration(seconds_to_run)
        cancel_fn = terminate_on_cancel(cancellable)

        triggerable = Triggerable()
        triggerable.triggered = True
        trigger_task = new_triggered_task(triggerable, duration=1.0, start=start, run=run, stop=stop,
                                          cancel_func=cancel_fn)

        # noinspection PyTypeChecker
        asyncio.run(trigger_task())

        assert start_count == 1
        assert stop_count == 1

    def test_triggered_task_can_be_retriggered(self) -> None:
        """
        Validates the task can be triggered a second time once the first trigger
        has completed.
        """
        seconds_to_run: int = 2

        start_count = 0

        async def restart():
            await asyncio.sleep(1.2)
            triggerable.triggered = True

        async def start():
            nonlocal start_count
            start_count += 1
            delayed_restart = asyncio.create_task(restart())

        cancellable = CancellableDuration(seconds_to_run)
        cancel_fn = terminate_on_cancel(cancellable)

        triggerable = Triggerable()
        triggerable.triggered = True
        trigger_task = new_triggered_task(triggerable, duration=1.0, start=start, cancel_func=cancel_fn)

        # noinspection PyTypeChecker
        asyncio.run(trigger_task())

        assert start_count == 2


class TestTriggerTimedEvents:
    def test_calling_start(self) -> None:
        """
        Validates that calling start works when called once, twice or more times.
        In these tests, there are no events to fire so it is a basic test. More
        complex tests are performed later.
        """
        trigger = TriggerTimedEvents()
        assert not trigger.running
        assert len(trigger.events) == 0

        # Start the trigger
        trigger.start()
        assert trigger.running
        assert len(trigger.events) == 0

        # Calling start a second time should have no effect
        trigger.start()
        assert trigger.running
        assert len(trigger.events) == 0

        # And calling it a third time should have no effect
        trigger.start()
        assert trigger.running
        assert len(trigger.events) == 0

    def test_calling_start_multiple_times(self) -> None:
        """
        Validates that calling start works when called once, twice or more times.
        In these tests there are events to fire. It also validates that calling
        start multiple times does not affect the timing of events.
        """
        trigger = TriggerTimedEvents()
        trigger.add_event(0, 90)
        trigger.add_event(99, 99)
        assert not trigger.running
        assert len(trigger.events) == 2

        # Start the trigger which should immediately fire one event.
        trigger.start()
        assert trigger.running
        assert len(trigger.events) == 2
        events = trigger.run()
        assert trigger.running
        assert len(events) == 1
        assert events[0].event == 90

        # Starting the trigger again should result in no more additional events.
        trigger.start()
        assert trigger.running
        assert len(trigger.events) == 2
        events = trigger.run()
        assert len(events) == 0

    def test_calling_stop_when_not_started(self) -> None:
        """
        Validates that calling stop works even when the trigger is not running.
        """
        trigger = TriggerTimedEvents()
        assert not trigger.running
        assert len(trigger.events) == 0

        # Stop the trigger, nothing should happen.
        trigger.stop()
        assert not trigger.running
        assert len(trigger.events) == 0

        # Stop the trigger again, again nothing should happen.
        trigger.stop()
        assert not trigger.running
        assert len(trigger.events) == 0

    def test_calling_stop_when_running(self) -> None:
        """
        Validates that calling stop on a running trigger will cancel any events
        that are queued up to run.
        """
        trigger = TriggerTimedEvents()
        trigger.add_event(0, 90)
        trigger.add_event(99, 99)
        assert not trigger.running
        assert len(trigger.events) == 2

        # Start the trigger which should immediately make one event ready to fire (but don't call run)
        trigger.start()
        assert trigger.running
        assert len(trigger.events) == 2

        # Now stop the trigger which cancels the events. (we actually call reset() here to test it calls stop())
        trigger.reset()
        assert not trigger.running
        assert len(trigger.events) == 2

        # Call run() which should return no events.
        events = trigger.run()
        assert not trigger.running
        assert len(events) == 0

    def test_starting_and_stopping_multiple_times(self) -> None:
        """
        Validates that calling starting and stopping the trigger multiple times
        results in the events being triggered correctly each time.
        """
        trigger = TriggerTimedEvents()
        trigger.add_event(0, 90)
        trigger.add_event(0.1, 91)
        assert not trigger.running
        assert len(trigger.events) == 2

        # Start the trigger which should immediately fire one event.
        trigger.start()
        assert trigger.running
        assert len(trigger.events) == 2
        events = trigger.run()
        assert trigger.running
        assert len(events) == 1
        assert events[0].event == 90

        # Wait long enough that we should have another event ready to fire.
        time.sleep(0.2)

        # Stop the trigger, which cancels any remaining events
        trigger.stop()
        assert not trigger.running
        assert len(trigger.events) == 2

        # Call run which returns nothing
        events = trigger.run()
        assert not trigger.running
        assert len(events) == 0

        # Call start again and we should see a single event.
        trigger.start()
        assert trigger.running
        assert len(trigger.events) == 2
        events = trigger.run()
        assert trigger.running
        assert len(events) == 1
        assert events[0].event == 90

    def test_running_without_any_events(self) -> None:
        """
        Validates that the trigger can be run without any events registered.
        """
        trigger = TriggerTimedEvents()
        assert not trigger.running
        assert len(trigger.events) == 0

        # Start the trigger, this should indicate that the trigger is running.
        trigger.start()
        assert trigger.running
        assert len(trigger.events) == 0

        # Call run, which will detect there are no events and will stop the trigger.
        events = trigger.run()
        assert not trigger.running
        assert len(events) == 0

        # Now we will check that stop works with no events.
        # Start the trigger again, this should indicate that the trigger is running.
        trigger.start()
        assert trigger.running
        assert len(trigger.events) == 0

        trigger.stop()
        assert not trigger.running

    def test_running_with_a_single_event(self) -> None:
        """
        Validates that the trigger can be run with just a single event registered.
        """
        trigger = TriggerTimedEvents()
        trigger.add_event(0.1, 90)
        assert not trigger.running
        assert len(trigger.events) == 1

        # Start the trigger, this should indicate that the trigger is running.
        trigger.start()
        assert trigger.running
        assert len(trigger.events) == 1

        # Call run which will not see any expired events and everything continues to run
        events = trigger.run()
        assert trigger.running
        assert len(events) == 0

        # Pause long enough to guarantee the event will trigger
        time.sleep(0.2)

        # Call run again, which will detect there are is a single event which has fired
        # and return it. The trigger will also be marked as not running at this point.
        events = trigger.run()
        assert not trigger.running
        assert len(events) == 1
        assert events[0].event == 90

    def test_running_with_multiple_events_with_same_time(self) -> None:
        """
        Validates that the trigger can be run with multiple events registered
        for the same time.
        """
        trigger = TriggerTimedEvents()
        trigger.add_event(0.05, 91)
        trigger.add_event(0.05, 90)
        assert not trigger.running
        assert len(trigger.events) == 2

        # Start the trigger, this should indicate that the trigger is running.
        trigger.start()
        assert trigger.running
        assert len(trigger.events) == 2

        # Pause long enough to guarantee the events will trigger
        time.sleep(0.15)

        # Call run, which will detect there are two events which have fired and
        # return them. The trigger will also be marked as not running at this point.
        events = trigger.run()
        assert not trigger.running
        assert len(events) == 2
        assert set([event.event for event in events]) == {90, 91}

    def test_running_with_multiple_events_with_different_times(self) -> None:
        """
        Validates that the trigger can be run with multiple events registered
        for multiple times.
        """
        trigger = TriggerTimedEvents()
        trigger.add_event(0, 90)
        trigger.add_event(0.08, 13)
        trigger.add_event(0.1, 81)
        trigger.add_event(0.1, 82)
        trigger.add_event(0.3, 103)
        assert not trigger.running
        assert len(trigger.events) == 5

        # Start the trigger, this should indicate that the trigger is running.
        trigger.start()
        assert trigger.running
        assert len(trigger.events) == 5

        # The first event fires straight away.
        events = trigger.run()
        assert trigger.running
        assert len(events) == 1
        assert events[0].event == 90

        # Pause long enough to guarantee the next events will trigger but leaving 1.
        time.sleep(0.2)

        # Call run, which will detect there are three events which have fired and
        # return them. The trigger will still be running at this point.
        events = trigger.run()
        assert trigger.running
        assert len(events) == 3
        assert set([event.event for event in events]) == {13, 81, 82}

        # Pause long enough to guarantee the last event will trigger but leaving 1.
        time.sleep(0.2)

        # Call run, which will detect there is a single event which has fired and
        # return it. The trigger will also be marked as not running at this point.
        events = trigger.run()
        assert not trigger.running
        assert len(events) == 1
        assert events[0].event == 103
