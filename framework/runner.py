import asyncio
import time

from framework.debug import info, warn, error

# collections.abc is not available in CircuitPython.
try:
    from collections.abc import Callable, Awaitable
except ImportError:
    pass


async def empty_callback() -> None:
    """
    A simple empty callback that does nothing and is used if no user callback is provided.
    """
    pass


class Runner:
    """
    Runner is used to run a set of asynchronous background tasks, providing a configurable
    amount of error handling based on the properties.

    By default, if any of the background tasks raises an exception, all other tasks will be
    cancelled and the runner will terminate. This can be controlled with self.cancel_on_exception.

    The runner can be provided a callback which will be called (roughly) the desired number
    of times per second. This callback can perform any task but will typically be used to
    cancel the runner. This can be achieved by setting self.cancel = True. The frequency the
    callback is actually called will be determined by the other background tasks.

    Background tasks to be run can be added with add_task(). All tasks should be added prior
    to calling run() because any added when run() is executing will not be started.

    Where a task completes, the framework will not (by default) restart the task. This behaviour
    is controlled by self.restart_on_completion. Setting self.restart_on_completion to true
    will cause the tasks to restart upon completion.

    Where a task errors with an exception, the framework normally cancels the runner. It is
    possible to get the runner to restart tasks that error by turning setting
    self.restart_on_exception = True. This will override self.cancel_on_exception.
    """
    DEFAULT_CALLBACK_FREQUENCY = 20  # How many times we expect the callback to be called per second.
    DEFAULT_CALLBACK_INTERVAL = 1 / DEFAULT_CALLBACK_FREQUENCY

    def __init__(self):
        self.__running = False
        self.cancel = False
        self.cancel_on_exception = True
        self.restart_on_exception = False
        self.restart_on_completion = False
        self.callback_interval = self.DEFAULT_CALLBACK_INTERVAL
        self.__tasks_to_run: list[Callable[[], Awaitable[None]]] = []

    def add_task(self, task: Callable[[], Awaitable[None]]) -> None:
        """
        Adds a task to the set of background tasks to run.
        :param task: The task to add.
        """
        self.__tasks_to_run.append(task)

    def run(self, callback: Callable[[], Awaitable[None]] = None) -> None:
        """
        Runs the framework. This creates an asynchronous task for all configured background
        tasks, allowing them all to run concurrently. It will also call the passed in callback
        function the desired number of times per second (defaulting to DEFAULT_CALLBACK_FREQUENCY).
        The callback can terminate the framework by setting runner.cancel = True.

        :param callback: This is called once every cycle based on the callback frequency.
        """
        if self.__running:
            raise Exception("Already running")

        # If no callback is specified then default.
        if callback is None:
            callback: Callable[[], Awaitable[None]] = empty_callback

        self.cancel = False
        try:
            asyncio.run(self.__execute(callback))
        except Exception as e:
            error(f'run(): Exception caught running framework: {e}')
            from framework.debug import stacktrace
            stacktrace(e)  # TODO: Remove
        finally:
            self.__running = False

    def __new_background_handler(self, func: Callable[[], Awaitable[None]]) -> (
            Callable)[[], Awaitable[None]]:
        async def the_task():
            while not self.cancel:
                try:
                    # TODO: Remove
                    await asyncio.sleep(0.5)
                    break
                    await func()

                except asyncio.CancelledError:
                    error(f'Caught CancelledError exception in the execute loop!')
                    # TODO: Handler cancel

                except Exception as e:
                    error(f'Caught the following exception in the execute loop: {e}!')
                    # TODO: handle exception

        return the_task

    async def __execute(self, callback: Callable[[], Awaitable[None]]) -> None:
        """
        Performs the actual coordination of the background tasks; including invoking
        the (potentially) user provided callback.

        :param callback: This is called once every cycle based on the callback frequency.
        """
        interval: int = int(self.callback_interval * 1000000000)
        next_callback = time.monotonic_ns()

        # TODO: Used to force termination in testing
        debug_cutoff: int = 0

        async def callback_task() -> None:
            # TODO: Wrap in the background_task_handle.
            nonlocal debug_cutoff
            nonlocal interval, next_callback
            while not self.cancel:
                # The callback always gets called first.
                if time.monotonic_ns() >= next_callback:
                    next_callback += interval
                    await callback()

                await asyncio.sleep(self.callback_interval)  # TODO: Different interval

                print(f'Callback task {self.cancel}')

                # TODO: remove Debug cutoff
                debug_cutoff += 1
                if debug_cutoff >= 5:
                    self.cancel = True

        async def background_task() -> None:
            nonlocal tasks
            while not self.cancel:
                await asyncio.sleep(self.callback_interval)  # TODO: Different interval

                done, cancelled, pending = set(), set(), set()
                for task in tasks:
                    # if task.done()
                    # if task.exception()
                    # if task.cancelled()
                    # if task.cancelling()
                    if task.done():
                        done.add(task)
                    elif task.cancelled():
                        cancelled.add(task)
                    else:
                        pending.add(task)

                print(f'Background task {self.cancel}, {len(done)}, {len(cancelled)}, {len(pending)}')

                if len(done) == len(tasks):
                    self.cancel = True

        # TODO: Start from beginnings of tests to build up working functionality.

        tasks: list[asyncio.Task] = [
            asyncio.create_task(self.__new_background_handler(task)()) for task in self.__tasks_to_run]

        # TODO: wrap in try-except block
        await asyncio.gather(*tasks, asyncio.create_task(background_task()), asyncio.create_task(callback_task()))

        # Now cancel any remaining tasks
        try:
            info(f'Cancelling {len(tasks)} tasks:')
            for task in tasks:
                info(f'  {task}')
                task.cancel()

        except asyncio.CancelledError:
            error(f'Caught CancelledError exception cancelling tasks!')

        except Exception as e:
            error(f'Caught the following exception cancelling tasks: {e}!')


async def __execute_orig(self, callback: Callable[[], Awaitable[None]]) -> None:
    tasks: dict[asyncio.Task, callback: Callable[[], Awaitable[None]]] = \
        dict((asyncio.create_task(task()), task) for task in self.__tasks_to_run)

    try:
        interval: int = int(self.callback_interval * 1000000000)
        next_callback = time.monotonic_ns()

        while not self.cancel:
            # The callback always gets called first.
            if time.monotonic_ns() >= next_callback:
                next_callback += interval
                await callback()

            if not tasks:
                self.cancel = True

            # If the callback set the cancel property then we stop processing.
            if self.cancel:
                continue

            # from framework import async_utils
            # done, pending = await async_utils.wait(tasks, timeout=0)
            done, pending = await asyncio.wait(tasks, timeout=0)

            for task in done:
                if task.exception():
                    warn(f'Exception: {task.exception()} raised by task {task}')

                    if self.restart_on_exception:
                        warn(f'Rerunning...')
                        function = tasks[task]
                        new_task = asyncio.create_task(function())
                        tasks[new_task] = function
                        pending.add(new_task)

                    elif self.cancel_on_exception:
                        self.cancel = True

                else:
                    info(f'Result: {task.result()} returned by task {task}')
                    if self.restart_on_completion:
                        info(f'Rerunning...')
                        function = tasks[task]
                        new_task = asyncio.create_task(function())
                        tasks[new_task] = function
                        pending.add(new_task)

                del tasks[task]

            if not pending:
                self.cancel = True

    except asyncio.CancelledError:
        error(f'Caught CancelledError exception in the execute loop!')

    except Exception as e:
        error(f'Caught the following exception in the execute loop: {e}!')

    # Now cancel any remaining tasks
    try:
        info(f'Cancelling {len(tasks)} tasks:')
        for task in tasks:
            info(f'  {task}')
            task.cancel()

    except asyncio.CancelledError:
        error(f'Caught CancelledError exception cancelling tasks!')

    except Exception as e:
        error(f'Caught the following exception cancelling tasks: {e}!')


def run(callback: Callable[[], Awaitable[None]] = None) -> None:
    """
    Runs the framework using default settings and configuration from config.toml file.

    :param callback: This is called once every cycle based on the callback frequency.
    """
    runner = Runner()
    # TODO: Load settings from config.toml file if present.
    # TODO: Setup runner with configuration from config.toml.
    runner.run(callback)
