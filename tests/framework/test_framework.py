import asyncio
import time
from collections.abc import Callable, Awaitable

import pytest

from framework.runner import Runner


def new_test_async_function(delay: float, name: str = "dummy", error: str = None) -> Callable[[], Awaitable[None]]:
    """
    Constructs a test async function that awaits for a predefined time then finishes.
    The async function can optionally raise an exception before terminating.

    :param delay: The number of seconds to sleep for.
    :param name: The name of the test function.
    :param error: If specified, an exception will be raised with this error.
    :return: A test async function that awaits for a predefined time then finishes (or raises an exception).
    """

    async def dummy():
        try:
            await asyncio.sleep(delay)

            if error:
                raise Exception(f'Test async function "{name}" has raised exception "{error}"...')

        except asyncio.CancelledError:
            pass

    return dummy


class TestRunner:
    def test_constructed_runner(self) -> None:
        """
        Check that the constructed instance has the expected set of attributes
        with the expected set of values.
        """
        runner = Runner()
        assert hasattr(runner, "cancel")
        assert hasattr(runner, "cancel_on_exception")
        assert hasattr(runner, "callback_interval")

        assert not runner.cancel
        assert runner.cancel_on_exception
        assert runner.callback_interval == Runner.DEFAULT_CALLBACK_INTERVAL

    def test_run_with_no_tasks(self) -> None:
        """
        Checks that the runner runs without any tasks and terminates.
        """
        runner = Runner()
        runner.run()
        assert runner.cancel

    def test_run_with_no_tasks_immediate_cancel(self) -> None:
        """
        Checks that the runner runs without any tasks with a callback that immediately
        cancels the runner and it terminates.
        """

        async def callback():
            runner.cancel = True

        runner = Runner()
        runner.run(callback)
        assert runner.cancel

    def test_run_with_single_background_task_that_finishes(self) -> None:
        """
        Checks that the runner runs the single background task and terminates.
        The background task will be expected to be called.
        """
        called = False

        async def task():
            nonlocal called
            called = True

        runner = Runner()
        runner.add_task(task)
        runner.run()
        assert runner.cancel
        assert called

    def test_adding_the_same_background_task_twice(self) -> None:
        """
        The same background task is added twice so each should be called
        and increment the called_count variable.
        """
        called_count = 0

        async def task():
            nonlocal called_count
            called_count += 1

        runner = Runner()
        runner.add_task(task)
        runner.add_task(task)
        runner.run()
        assert runner.cancel
        assert called_count == 2

    def test_adding_two_background_tasks_both_get_called(self) -> None:
        """
        Two different background tasks are added so each should be called.
        Both should complete.
        """
        called1 = False
        called2 = False

        async def task1():
            nonlocal called1
            called1 = True

        async def task2():
            nonlocal called2
            called2 = True

        runner = Runner()
        runner.add_task(task1)
        runner.add_task(task2)
        runner.run()
        assert runner.cancel
        assert called1
        assert called2

    def test_run_with_single_background_task_and_cancel(self) -> None:
        """
        Runs a background task that should execute for 999 seconds.
        The callback will terminate after it is called 5 times.
        """
        called_count: int = 0

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= 5

        runner = Runner()
        runner.add_task(new_test_async_function(999))
        runner.run(callback)
        assert runner.cancel
        assert called_count == 5

    @pytest.mark.skip(reason="suppressed while rewriting Runner class to also work on CircuitPython")
    def test_run_invokes_callback_with_sensible_frequency(self) -> None:
        """
        This test allows the callback to be called the same number of times
        as the default callback frequency and validates that we are within
        a tolerance of 3%. At the same time, a busy blocking background task
        is running which prevents the dumb method of sleeping from working.
        """
        called_count: int = 0
        seconds_to_run: int = 2

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= (seconds_to_run * Runner.DEFAULT_CALLBACK_FREQUENCY)

        async def blocking_task():
            while True:
                # Sleep for 50ms whilst blocking.
                time.sleep(0.050)
                # Sleep for 50ms whilst NOT blocking.
                await asyncio.sleep(0.050)

        runner = Runner()
        runner.add_task(blocking_task)
        start = time.time()
        runner.run(callback)
        end = time.time()

        assert runner.cancel
        assert called_count == seconds_to_run * Runner.DEFAULT_CALLBACK_FREQUENCY
        assert (end - start) < (seconds_to_run * 1.03)
        assert (end - start) > (seconds_to_run * 0.97)

    @pytest.mark.skip(reason="suppressed while rewriting Runner class to also work on CircuitPython")
    def test_callback_always_gets_called_first(self):
        """
        Checks that the callback gets called first. In this test, the callback
        immediately cancels the runner so the background task should not get
        invoked at all.
        """
        callback_time = None
        task_time = None

        async def callback():
            nonlocal callback_time
            callback_time = time.time()
            runner.cancel = True

        async def task():
            nonlocal task_time
            task_time = time.time()

        runner = Runner()
        runner.add_task(task)
        runner.run(callback)

        assert callback_time is not None
        assert task_time is None

    @pytest.mark.skip(reason="suppressed while rewriting Runner class to also work on CircuitPython")
    def test_run_with_exception_in_task_default_behavior(self) -> None:
        """
        Run 4 background tasks with one that raises an exception.
        The exception should initiate cancellation of the other tasks.
        The callback should only get called once as the exception is
        immediate.
        """
        called_count: int = 0

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= 5

        runner = Runner()
        runner.add_task(new_test_async_function(999))
        runner.add_task(new_test_async_function(999))
        runner.add_task(new_test_async_function(0, error="deliberate"))
        runner.add_task(new_test_async_function(999))
        runner.run(callback)

        assert runner.cancel
        assert called_count == 1

    @pytest.mark.skip(reason="suppressed while rewriting Runner class to also work on CircuitPython")
    def test_run_with_exception_in_task_cancel_on_exception_on(self) -> None:
        """
        Run 4 background tasks with one that raises an exception.
        The exception should initiate cancellation of the other tasks.
        The callback should only get called once as the exception is
        immediate.
        """
        called_count: int = 0

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= 5

        runner = Runner()
        runner.cancel_on_exception = True
        runner.add_task(new_test_async_function(999))
        runner.add_task(new_test_async_function(999))
        runner.add_task(new_test_async_function(0, error="deliberate"))
        runner.add_task(new_test_async_function(999))
        runner.run(callback)

        assert runner.cancel
        assert called_count == 1

    @pytest.mark.skip(reason="suppressed while rewriting Runner class to also work on CircuitPython")
    def test_run_with_exception_in_task_cancel_on_exception_off(self) -> None:
        """
        Run 4 background tasks with one that raises an exception.
        The exception will not cause cancellation of the other tasks.
        The callback should get called the full 5 times.
        """
        called_count: int = 0

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= 5

        runner = Runner()
        runner.cancel_on_exception = False
        runner.add_task(new_test_async_function(999))
        runner.add_task(new_test_async_function(999))
        runner.add_task(new_test_async_function(0, error="deliberate"))
        runner.add_task(new_test_async_function(999))
        runner.run(callback)

        assert runner.cancel
        assert called_count == 5

    @pytest.mark.skip(reason="suppressed while rewriting Runner class to also work on CircuitPython")
    def test_restart_on_task_completion_single(self) -> None:
        """
        Run a single background task that simply terminates. The framework will
        rerun it allowing it to continue to increment the counter.
        """
        called_count: int = 0
        task_count: int = 0

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= 2

        async def task():
            nonlocal task_count
            task_count += 1

        runner = Runner()
        runner.restart_on_completion = True
        runner.add_task(task)
        runner.run(callback)

        assert runner.cancel
        assert called_count == 2
        # The actual number of tasks completed will be a lot but depends on the
        # computers' performance.
        assert task_count > 10

    @pytest.mark.skip(reason="suppressed while rewriting Runner class to also work on CircuitPython")
    def test_restart_on_task_completion_multiple(self) -> None:
        """
        Runs several background task that simply terminate. The framework will
        rerun them allowing them to continue to increment the counters.
        """
        called_count: int = 0
        task1_count: int = 0
        task2_count: int = 0
        task3_count: int = 0

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= 2

        async def task1():
            nonlocal task1_count
            task1_count += 1
            await asyncio.sleep(0.001)

        async def task2():
            nonlocal task2_count
            task2_count += 1
            await asyncio.sleep(0.005)

        async def task3():
            nonlocal task3_count
            task3_count += 1
            await asyncio.sleep(0.010)

        runner = Runner()
        runner.restart_on_completion = True
        runner.add_task(new_test_async_function(999))
        runner.add_task(task1)
        runner.add_task(task2)
        runner.add_task(new_test_async_function(999))
        runner.add_task(task3)
        runner.add_task(new_test_async_function(999))
        runner.run(callback)

        assert runner.cancel
        assert called_count == 2
        # The actual number of tasks completed will be a lot but depends on the
        # computers' performance.
        assert task1_count > 10
        assert task2_count > 10
        assert task3_count > 10

    @pytest.mark.skip(reason="suppressed while rewriting Runner class to also work on CircuitPython")
    def test_restart_on_exception_single(self) -> None:
        """
        Run a single background task that raises an exception. The framework will
        rerun it allowing it to continue to increment the counter.
        """
        called_count: int = 0
        task_count: int = 0

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= 2

        async def task():
            nonlocal task_count
            task_count += 1
            raise Exception("Failed!")

        runner = Runner()
        runner.restart_on_exception = True
        runner.add_task(task)
        runner.run(callback)

        assert runner.cancel
        assert called_count == 2
        # The actual number of tasks completed will be a lot but depends on the
        # computers' performance.
        assert task_count > 10

    @pytest.mark.skip(reason="suppressed while rewriting Runner class to also work on CircuitPython")
    def test_restart_on_exception_multiple(self) -> None:
        """
        Runs several background task raise exceptions. The framework will
        rerun them allowing them to continue to increment the counters.
        """
        called_count: int = 0
        task1_count: int = 0
        task2_count: int = 0
        task3_count: int = 0

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= 2

        async def task1():
            nonlocal task1_count
            task1_count += 1
            await asyncio.sleep(0.001)
            raise Exception("Failed!")

        async def task2():
            nonlocal task2_count
            task2_count += 1
            await asyncio.sleep(0.005)
            raise Exception("Failed!")

        async def task3():
            nonlocal task3_count
            task3_count += 1
            await asyncio.sleep(0.010)
            raise Exception("Failed!")

        runner = Runner()
        runner.restart_on_exception = True
        runner.add_task(new_test_async_function(999))
        runner.add_task(task1)
        runner.add_task(task2)
        runner.add_task(new_test_async_function(999))
        runner.add_task(task3)
        runner.add_task(new_test_async_function(999))
        runner.run(callback)

        assert runner.cancel
        assert called_count == 2
        # The actual number of tasks completed will be a lot but depends on the
        # computers' performance.
        assert task1_count > 10
        assert task2_count > 10
        assert task3_count > 10

    @pytest.mark.skip(reason="suppressed while rewriting Runner class to also work on CircuitPython")
    def test_restart_on_exception_and_completion_multiple(self) -> None:
        """
        Runs lots of background tasks that raise exceptions, complete or run forever.
        The framework will rerun them allowing them to continue to increment the counters.
        """
        called_count: int = 0
        task1_count: int = 0
        task2_count: int = 0
        task3_count: int = 0
        task4_count: int = 0

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= 2

        async def task1():
            nonlocal task1_count
            task1_count += 1
            await asyncio.sleep(0.001)
            raise Exception("Failed!")

        async def task2():
            nonlocal task2_count
            task2_count += 1
            await asyncio.sleep(0.005)

        async def task3():
            nonlocal task3_count
            task3_count += 1
            await asyncio.sleep(0.010)
            raise Exception("Failed!")

        async def task4():
            nonlocal task4_count
            task4_count += 1
            await asyncio.sleep(0.005)

        runner = Runner()
        runner.restart_on_completion = True
        runner.restart_on_exception = True
        runner.add_task(new_test_async_function(0.0001))
        runner.add_task(new_test_async_function(999))
        runner.add_task(new_test_async_function(0.0010))
        runner.add_task(task1)
        runner.add_task(new_test_async_function(0.0005))
        runner.add_task(task2)
        runner.add_task(new_test_async_function(999))
        runner.add_task(new_test_async_function(0.0050))
        runner.add_task(task3)
        runner.add_task(new_test_async_function(0.0020))
        runner.add_task(task4)
        runner.add_task(new_test_async_function(999))
        runner.add_task(new_test_async_function(0.0002))
        runner.run(callback)

        assert runner.cancel
        assert called_count == 2
        # The actual number of tasks completed will be a lot but depends on the
        # computers' performance.
        assert task1_count > 10
        assert task2_count > 10
        assert task3_count > 10
        assert task4_count > 10
