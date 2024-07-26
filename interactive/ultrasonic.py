from interactive.environment import is_running_on_desktop
from interactive.polyfills.ultrasonic import Ultrasonic
from interactive.runner import Runner
from interactive.scheduler import new_scheduled_task, terminate_on_cancel

# collections.abc is not available in CircuitPython.
if is_running_on_desktop():
    from collections.abc import Callable, Awaitable


class UltrasonicTrigger:
    """
    UltrasonicTrigger triggers events based on the distances returned from an
    Ultrasonic sensor. The user can specify what distances they want to get
    trigger notifications for. These events are triggered when the distance is
    less than the specified trigger distance. Events can be set to be triggered
    once (with a specified reset time). A reset duration of zero effectively
    results in continuous notifications.

    Instances of this class will need to register() with a Runner in order to work.
    """

    class __Trigger:
        """
        Holds the state of a trigger.
        """

        def __init__(self, distance, handler, reset):
            self.distance = distance
            self.handler = handler
            self.reset = reset
            self.triggered = 0.0
            self.reset_time = 0.0

    def __init__(self, ultrasonic: Ultrasonic):
        if ultrasonic is None:
            raise ValueError("ultrasonic cannot be None")

        if not isinstance(ultrasonic, Ultrasonic):
            raise ValueError("ultrasonic must be of type Ultrasonic")

        self.__runner = None
        self.__ultrasonic = ultrasonic
        self.__triggers = []

    def add_trigger(self, distance: int, handler: Callable[[float], Awaitable[None]] = None, reset: float = 60.0):
        """
        Adds a trigger to fire when the distance sensor returns a distance under
        the trigger distance. If the specified handler is None, it removes all
        triggers for that distance.

        :param distance: The distance which will trigger the event
        :param handler:  The callback function to be called for this trigger.
                         It gets passed the distance from the ultrasonic sensor.
        :param reset:    The time in seconds that the trigger will be reset so
                        that it can fire again.
        """

        if handler is None:
            self.__triggers = [trigger for trigger in self.__triggers if trigger.distance != distance]
        else:
            self.__triggers.append(self.__Trigger(distance, handler, reset))

    def reset_triggers(self):
        pass

    def register(self, runner: Runner) -> None:
        """
        Registers this Ultrasonic instance as a task with the provided Runner
        and schedules a background task to be called at a regular frequency.

        :param runner: the runner to register with.
        """

        async def handler() -> None:
            self.__check_ultrasonic()

        self.__runner = runner
        # Add a scheduled task for checking the distance sensor and triggering events.
        scheduled_task = new_scheduled_task(handler, terminate_on_cancel(self.__runner), 2)
        runner.add_loop_task(scheduled_task)

    def __check_ultrasonic(self):
        """
        The internal loop checks the sensor against the trigger settings firing an
        event if it detects an object closer than the trigger distances.
        """
        if not self.__runner.cancel:
            self.reset_triggers()

            # TODO: Check distance and fire triggers.
