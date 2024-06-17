import asyncio
import time

from framework.debug import debug, info, warn, error

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

    # This is used to control the sleep interval used in the internal coordination loops.
    __INTERNAL_BACKGROUND_LOOP_SLEEP_INTERVAL = 0.0001

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
        finally:
            self.__running = False

    async def __execute(self, callback: Callable[[], Awaitable[None]]) -> None:
        """
        Performs the actual coordination of the background tasks; including invoking
        the (potentially) user provided callback.

        :param callback: This is called once every cycle based on the callback frequency.
        """

        async def background_task() -> None:
            nonlocal tasks
            while not self.cancel:
                await asyncio.sleep(self.__INTERNAL_BACKGROUND_LOOP_SLEEP_INTERVAL)

                done, cancelled, pending = set(), set(), set()
                for task in tasks:
                    if task.done():
                        done.add(task)
                    elif task.cancelled():
                        cancelled.add(task)
                    else:
                        pending.add(task)

                debug(
                    f'Background tasks: Done: {len(done)}, Cancelled: {len(cancelled)}, Pending: {len(pending)}, '
                    f'Cancel: {self.cancel}')

                if len(done) >= len(tasks):
                    self.cancel = True

            # Now cancel all background tasks.
            # TODO: Remove the duplication of cancelling code.
            info(f'Cancelling {len(tasks)} tasks:')
            if self.cancel:
                for task in tasks:
                    info(f'  {task}')
                    task.cancel()

        tasks: list[asyncio.Task] = [
            asyncio.create_task(self.__new_task_handler(task)()) for task in self.__tasks_to_run]

        # TODO: wrap in try-except block
        await asyncio.gather(
            asyncio.create_task(self.__new_callback_handler(callback)()),
            asyncio.create_task(background_task()),
            *tasks)

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

    def __new_task_handler(self, task: Callable[[], Awaitable[None]]) -> Callable[[], Awaitable[None]]:
        """
        This wraps any task and provides the exception and completion handling
        such as restart as defined by the Runners properties.

        :param task: The task that is to be wrapped.
        """

        async def handler():
            while not self.cancel:
                try:
                    # This sleep both delays the start of the handler but also throttles the
                    # task if it gets into a greedy loop where it does not await itself. This
                    # can happen if the task keeps ending with restarts on or if it keeps
                    # raising exceptions.
                    await asyncio.sleep(self.__INTERNAL_BACKGROUND_LOOP_SLEEP_INTERVAL)
                    await task()
                    info(f'Task completed {task}')

                    if self.restart_on_completion:
                        info(f'Rerunning task {task}')
                    else:
                        break

                except asyncio.CancelledError:
                    error(f'Caught CancelledError exception for task {task}')
                    break

                except Exception as e:
                    warn(f'Exception: {e} raised by task {task}')

                    if self.restart_on_exception:
                        warn(f'Rerunning task {task}')

                    elif self.cancel_on_exception:
                        self.cancel = True

        return handler

    def __new_callback_handler(self, callback: Callable[[], Awaitable[None]]) -> Callable[[], Awaitable[None]]:
        """
        Performs the scheduling and invocation of the (potentially) user provided callback.
        If the callback raises an exception then the Runner will be set to cancel; irrespective
        of the rest of the runner configuration.

        :param callback: This is called once every cycle based on the callback frequency.
        """
        interval: int = int(self.callback_interval * 1000000000)
        next_callback = time.monotonic_ns()

        async def handler() -> None:
            nonlocal interval, next_callback
            while not self.cancel:
                if time.monotonic_ns() >= next_callback:
                    next_callback += interval
                    debug(f'calling callback function')

                    try:
                        await callback()

                    except asyncio.CancelledError:
                        error(f'Caught CancelledError exception for callback, cancelling runner')
                        self.cancel = True

                    except Exception as e:
                        error(f'Exception: {e} raised by callback, cancelling runner')
                        self.cancel = True

                await asyncio.sleep(self.callback_interval / 64)

        return handler


def run(callback: Callable[[], Awaitable[None]] = None) -> None:
    """
    Runs the framework using default settings and configuration from config.toml file.

    :param callback: This is called once every cycle based on the callback frequency.
    """
    runner = Runner()
    # TODO: Load settings from config.toml file if present.
    # TODO: Setup runner with configuration from config.toml.
    runner.run(callback)
