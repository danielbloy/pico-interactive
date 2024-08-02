from interactive.runner import Runner


class AudioController:
    def __init__(self):
        self.__runner = None

    def register(self, runner: Runner) -> None:
        """
        Registers this AudioController instance as a task with the provided Runner.

        :param runner: the runner to register with.
        """
        self.__runner = runner
        runner.add_loop_task(self.__loop)

    async def __loop(self):
        """
        The internal loop simply invokes the correct handler based on the button state.
        """
        if not self.__runner.cancel:
            # TODO: Implement
            pass
