import asyncio

from interactive.configuration import REPORT_RAM
from interactive.control import RUNNER_DEFAULT_CALLBACK_FREQUENCY, SCHEDULER_INTERNAL_LOOP_RATIO
from interactive.environment import is_running_on_desktop
from interactive.log import debug, info, warn, error, stacktrace
from interactive.memory import report_memory_usage
from interactive.scheduler import new_scheduled_task, terminate_on_cancel, new_loop_task

# collections.abc is not available in CircuitPython.
if is_running_on_desktop():
    from collections.abc import Callable, Awaitable


async def empty_callback() -> None:
    """
    A simple empty callback that does nothing and is used if no user callback is provided.
    """
    pass


async def report_memory() -> None:
    report_memory_usage("Runner run()")


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

    Where a task completes, the interactive will not (by default) restart the task. This behaviour
    is controlled by self.restart_on_completion. Setting self.restart_on_completion to true
    will cause the tasks to restart upon completion.

    Where a task errors with an exception, the interactive normally cancels the runner. It is
    possible to get the runner to restart tasks that error by turning setting
    self.restart_on_exception = True. This will override self.cancel_on_exception.
    """

    def __init__(self, callback_frequency=RUNNER_DEFAULT_CALLBACK_FREQUENCY):
        self.__running = False
        self.cancel = False
        self.cancel_on_exception = True
        self.restart_on_exception = False
        self.restart_on_completion = False
        self.callback_frequency = callback_frequency
        self.__tasks_to_run: list[Callable[[], Awaitable[None]]] = []
        self.__internal_loop_sleep_interval = 0.0

    def add_task(self, task: Callable[[], Awaitable[None]]) -> None:
        """
        Adds a task to the set of background tasks to run.

        :param task: The task to add.
        """
        self.__tasks_to_run.append(task)

    def add_loop_task(self, task: Callable[[], Awaitable[None]]) -> None:
        """
        Adds a task to the set of background tasks to run; wrapping the
        callback in an infinite loop.

        :param task: The task to add, wrapped in an infinite loop.
        """
        self.__tasks_to_run.append(new_loop_task(task))

    def run(self, callback: Callable[[], Awaitable[None]] = None) -> None:
        """
        Runs the interactive. This creates an asynchronous task for all configured background
        tasks, allowing them all to run concurrently. It will also call the passed in callback
        function the desired number of times per second (defaulting to DEFAULT_CALLBACK_FREQUENCY).
        The callback can terminate the interactive by setting runner.cancel = True.

        :param callback: This is called once every cycle based on the callback frequency.
        """
        if self.__running:
            raise Exception("Already running")

        # If no callback is specified then default.
        if callback is None:
            callback: Callable[[], Awaitable[None]] = empty_callback

        self.cancel = False
        try:
            self.__internal_loop_sleep_interval = 1 / (self.callback_frequency * SCHEDULER_INTERNAL_LOOP_RATIO)
            asyncio.run(self.__execute(callback))
        except Exception as e:
            error(f'run(): Exception caught running interactive: {e}')
            stacktrace(e)

        finally:
            self.__running = False

    async def __execute(self, callback: Callable[[], Awaitable[None]]) -> None:
        """
        Performs the actual coordination of the background tasks; including invoking
        the (potentially) user provided callback.

        :param callback: This is called once every cycle based on the callback frequency.
        """

        tasks: list[asyncio.Task] = [
            asyncio.create_task(self.__new_task_handler(task)()) for task in self.__tasks_to_run]

        if REPORT_RAM:
            tasks.append(
                new_scheduled_task(report_memory, terminate_on_cancel(self), 1 / 5)())

        try:
            await asyncio.gather(
                asyncio.create_task(self.__new_scheduled_task_handler(callback)()),
                asyncio.create_task(self.__cancellation_handler(tasks)()),
                *tasks)

        except asyncio.CancelledError:
            error(f'Caught CancelledError exception cancelling tasks!')

        except Exception as e:
            error(f'Caught the following exception cancelling tasks: {e}!')
            stacktrace(e)

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
                    await self.__internal_loop_wait()
                    if not self.cancel:
                        await task()
                        info(f'Task completed {task}')

                    if self.restart_on_completion:
                        info(f'Rerunning task {task}')
                    else:
                        return

                except asyncio.CancelledError:
                    error(f'Caught CancelledError exception for task {task}')
                    return

                except Exception as e:
                    warn(f'Exception: {e} raised by task {task}')
                    stacktrace(e)

                    if self.restart_on_exception:
                        warn(f'Rerunning task {task}')

                    elif self.cancel_on_exception:
                        self.cancel = True

                    else:
                        return

        return handler

    def __new_scheduled_task_handler(self, task: Callable[[], Awaitable[None]]) -> Callable[[], Awaitable[None]]:
        """
        Performs the scheduling invocation of the provided callback based on self.callback_frequency.
        If the callback raises an exception then the Runner will be set to cancel; irrespective of
        the rest of the runner configuration. This is intended to be used to schedule tasks internal
        to the runner only (such as scheduling invocation of the callback).

        Note: This function will complete once it detects that self.cancel is set so cannot be used
              for cleanup during cancellation.

        :param task: Called once every cycle based on the callback frequency.
        """

        async def handler() -> None:
            try:
                if not self.cancel:
                    await task()

            except asyncio.CancelledError:
                error(f'Caught CancelledError exception for scheduled task {task}, cancelling runner')
                self.cancel = True

            except Exception as e:
                error(f'Exception: {e} raised by scheduled task {task}, cancelling runner')
                stacktrace(e)
                self.cancel = True

        return new_scheduled_task(handler, terminate_on_cancel(self), self.callback_frequency)

    async def __internal_loop_wait(self) -> None:
        """
        This is used to provide a delay to the internal async loops used to
        control the runner. It's a fraction of the timed interval.
        """
        await asyncio.sleep(self.__internal_loop_sleep_interval)

    def __cancel_tasks(self, tasks: list[asyncio.Task]) -> None:
        """
        Cancels all the specified tasks.

        :param tasks: The tasks to cancel.
        """
        self.cancel = True
        info(f'Cancelling {len(tasks)} tasks:')
        for task in tasks:
            info(f'  {task}')
            task.cancel()

    def __cancellation_handler(self, tasks: list[asyncio.Task]) -> Callable[[], Awaitable[None]]:
        """
        This handler runs in the background and monitors which tasks from the passed in
        list have completed. Once all have completed, the Runner will be cancelled.

        :param tasks: The list of background tasks to monitor.
        """

        async def wait_for_finished_tasks() -> None:
            nonlocal tasks

            completed: int = 0
            pending: int = 0
            for task in tasks:
                if task.done():
                    completed += 1
                    tasks.remove(task)
                else:
                    pending += 1

            debug(f'Background tasks: Done: {completed}, Pending: {pending}')

            # If all the tasks have completed then cancel the runner.
            if pending <= 0:
                self.cancel = True

        async def cancel_handler() -> None:
            nonlocal tasks

            # Monitor in the background for all tasks to complete.
            await self.__new_scheduled_task_handler(wait_for_finished_tasks)()

            debug(f'Pausing to allow the remaining {len(tasks)} tasks to complete...')
            # Loop, allowing all other tasks to complete after seeing self.cancel is set
            for i in range(len(tasks) * 2):
                await self.__internal_loop_wait()

            # Remove any tasks that have completed from the list.
            await wait_for_finished_tasks()

            # Cancel the remaining tasks.
            self.__cancel_tasks(tasks)

        return cancel_handler
