from interactive.polyfills.ultrasonic import Ultrasonic
from interactive.runner import Runner
from interactive.scheduler import new_scheduled_task, terminate_on_cancel


# TODO: Include trigger class based on ultrasonic.

class UltrasonicTrigger:
    """
    UltrasonicTrigger triggers events based on the distances returned from an
    Ultrasonic sensor. The user can

    Instances of this class will need to register() with a Runner in order to work.
    """

    def __init__(self, ultrasonic: Ultrasonic):
        if ultrasonic is None:
            raise ValueError("ultrasonic cannot be None")

        if not isinstance(ultrasonic, Ultrasonic):
            raise ValueError("ultrasonic must be of type Ultrasonic")

        self.__runner = None
        self.__ultrasonic = ultrasonic

    def register(self, runner: Runner) -> None:
        """
        Registers this Ultrasonic instance as a task with the provided Runner
        and schedules a background task to be called at a regular frequency.

        :param runner: the runner to register with.
        """

        async def handler() -> None:
            self.__check_ultrasonic()

        self.__runner = runner
        scheduled_task = new_scheduled_task(handler, terminate_on_cancel(self.__runner), 2)
        runner.add_loop_task(scheduled_task)

    async def __check_ultrasonic(self):
        """
        The internal loop checks the sensor against the trigger settingsm firing an
        event if it detects an object closer than the trigger distances.
        """
        if not self.__runner.cancel:
            pass
