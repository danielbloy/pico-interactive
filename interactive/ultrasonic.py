import time

from interactive.environment import is_running_on_desktop
from interactive.log import debug, info
from interactive.polyfills.ultrasonic import Ultrasonic, ULTRASONIC_MAX_DISTANCE
from interactive.runner import Runner
from interactive.scheduler import new_scheduled_task, terminate_on_cancel

# collections.abc is not available in CircuitPython.
if is_running_on_desktop():
    from collections.abc import Callable, Awaitable

DEFAULT_SAMPLE_FREQUENCY = 2  # 2 times for second
DEFAULT_RESET_INTERVAL = 60.0  # 60 seconds


class UltrasonicController:
    """
    UltrasonicController triggers events based on the distances returned from an
    Ultrasonic sensor. The user can specify what distances they want to get
    trigger notifications for. These events are triggered when the distance is
    less than the specified trigger distance. Events can be set to be triggered
    once (with a specified reset time). A reset duration of zero effectively
    results in continuous notifications.

    Instances of this class will need to register() with a Runner in order to work.
    """

    class __Trigger:
        """
        Holds the state of a trigger; included when it was last triggered and when
        it will expire so that it can trigger again
        """

        def __init__(self, distance, handler, reset_interval):
            self.distance = distance
            self.handler = handler
            self.reset_interval = reset_interval
            self.triggered_time = 0.0
            self.expiry_time = 0.0

    def __init__(self, ultrasonic: Ultrasonic, sample_frequency: int = DEFAULT_SAMPLE_FREQUENCY):
        """
        Constructs and instance of UltrasonicController that will sample the distance from the
        supplied Ultrasonic sensor at the specified frequency. Because of the time taken to
        sample a distance, it is recommended that the sample frequency does not exceed 6 and
        a sample frequency of 2 is adequate for the majority of situations.

        :param ultrasonic:       The Ultrasonic sensor to sample the distance from.
        :param sample_frequency: The frequency to sample the distance from the Ultrasonic sensor.
        """
        if ultrasonic is None:
            raise ValueError("ultrasonic cannot be None")

        if not isinstance(ultrasonic, Ultrasonic):
            raise ValueError("ultrasonic must be of type Ultrasonic")

        self.__runner = None
        self.__ultrasonic = ultrasonic
        self.__sample_frequency = sample_frequency
        self.__last_distance = ULTRASONIC_MAX_DISTANCE
        self.__triggers = []

    @property
    def distance(self) -> float:
        """
        Return the last distance measured by the sensor in cm. This property does
        NOT sample the distance from the Ultrasonic sensor.
        """
        return self.__last_distance

    def add_trigger(self, distance: int, handler: Callable[[float, float], Awaitable[None]] = None,
                    reset_interval: float = DEFAULT_RESET_INTERVAL):
        """
        Adds a trigger to fire when the distance sensor returns a distance under
        the trigger distance. If the specified handler is None, it removes all
        triggers for that distance.

        :param distance:       The distance which will trigger the event
        :param handler:        The callback function to be called for this trigger.
                               It gets passed the registered trigger distance as well
                               as the distance from the ultrasonic sensor.
        :param reset_interval: The time in seconds that the trigger will be reset so
                               that it can fire again.
        """

        if handler is None:
            self.__triggers = [trigger for trigger in self.__triggers if trigger.distance != distance]
        else:
            self.__triggers.append(self.__Trigger(distance, handler, reset_interval))

    def register(self, runner: Runner) -> None:
        """
        Registers this Ultrasonic instance as a task with the provided Runner
        and schedules a background task to be called at a regular frequency
        which will check the distance sensor and trigger events as they occur.
        As checking the distance sensor is an expensive blocking operation,
        it is only checked rarely.

        :param runner: The runner to register with.
        """

        async def handler() -> None:
            """
            Check the sensor against the trigger settings firing an event
            if it detects an object closer than the trigger distances.
            """
            if not self.__runner.cancel:
                now = time.monotonic()

                # As checking the sensor is expensive and blocking, we only do it
                # if we have a trigger that can trigger.
                expired_triggers = [trigger for trigger in self.__triggers if now >= trigger.expiry_time]
                if len(expired_triggers) <= 0:
                    debug(f"No triggers are available for triggering, skipping.")
                    return

                self.__last_distance = self.__ultrasonic.distance
                info(f"Distance from sensor {self.__last_distance}.")
                for trigger in self.__triggers:
                    if now >= trigger.expiry_time and self.__last_distance < trigger.distance:
                        trigger.triggered_time = now
                        trigger.expiry_time = now + trigger.reset_interval
                        await trigger.handler(trigger.distance, self.__last_distance)

        self.__runner = runner
        scheduled_task = (
            new_scheduled_task(
                handler,
                terminate_on_cancel(self.__runner),
                self.__sample_frequency))
        runner.add_task(scheduled_task)
