import asyncio
import time

from framework.control import SCHEDULER_DEFAULT_FREQUENCY
from framework.scheduler import never_terminate, terminate_on_cancel, new_scheduled_task


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

    def test_scheduled_task_never_called(self) -> None:
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

    def test_scheduled_task_stops(self) -> None:
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

    def test_scheduled_task_called_multiple_times(self) -> None:
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

    def test_run_invokes_callback_with_sensible_frequency(self) -> None:
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
            await asyncio.sleep(0.001)

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

    def test_run_invokes_callback_with_custom_frequency(self) -> None:
        """
        This test is the same as test_run_invokes_callback_with_sensible_frequency()
        but we specify a custom frequency instead.
        """
        called_count: int = 0
        seconds_to_run: int = 2
        frequency: int = 10

        async def task():
            nonlocal called_count
            called_count += 1
            await asyncio.sleep(0.001)

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
