from collections.abc import Callable, Awaitable

import pytest

from interactive.polyfills.ultrasonic import Ultrasonic, ULTRASONIC_MAX_DISTANCE
from interactive.runner import Runner
from interactive.ultrasonic import UltrasonicTrigger


class TestUltrasonic(Ultrasonic):
    def __init__(self):
        super().__init__(None, None)
        self.dist = 0.0
        self.dist_called_count = 0

    @property
    def distance(self) -> float:
        self.dist_called_count += 1
        return self.dist


class TestUltrasonicTrigger:

    def test_creating_with_none_ultrasonic_errors(self) -> None:
        """
        Validates that a UltrasonicTrigger cannot be constructed with
        a None value.
        """
        with pytest.raises(ValueError):
            # noinspection PyTypeChecker
            UltrasonicTrigger(None)

    def test_creating_with_string_errors(self) -> None:
        """
        Validates that a UltrasonicTrigger cannot be constructed with
        a value that is not a Ultrasonic.
        """
        with pytest.raises(ValueError):
            # noinspection PyTypeChecker
            UltrasonicTrigger("")

    def test_distance_does_not_call_sensor(self) -> None:
        """
        Validates that a new UltrasonicTrigger initialises the distance property
        to the default max distance and does not invoke the Ultrasonic distance
        sensor to calculate distance even when called.
        """
        ultrasonic = TestUltrasonic()
        trigger = UltrasonicTrigger(ultrasonic)

        ultrasonic.dist = 123.456
        assert trigger.distance == ULTRASONIC_MAX_DISTANCE
        assert ultrasonic.dist_called_count == 0

    def test_distance_returns_last_sensor_value(self) -> None:
        """
        Validates that the distance property returns the last distance value
        returned from the Ultrasonic sensor and does not sample it when called.
        This is a relatively complex test as it has to setup a full Runner and
        iteration of the runner loop that calls the Ultrasonic sensor.
        """
        called_count: int = 0

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= 2

        ultrasonic = TestUltrasonic()
        trigger = UltrasonicTrigger(ultrasonic)

        # Check that the initial value is correct.
        ultrasonic.dist = 123.456
        assert trigger.distance == ULTRASONIC_MAX_DISTANCE
        assert ultrasonic.dist_called_count == 0

        trigger_called_count = 0
        distance_value = -1.0
        actual_value = -1.0

        # A handler that will be triggered needs to be registered; we
        # also store the values it is called with.
        async def trigger_handler(distance: float, actual: float) -> None:
            nonlocal trigger_called_count, distance_value, actual_value
            trigger_called_count += 1
            distance_value = distance
            actual_value = actual

        trigger.add_trigger(500, trigger_handler, 5)

        # Run the runner for a single iteration; this will call the ultrasonic
        # sensor during that first iterations.
        runner = Runner()
        trigger.register(runner)
        runner.run(callback)

        # Validate the Ultrasonic sensor only got called once and the trigger also
        # only got called once.
        assert ultrasonic.dist_called_count == 1
        assert trigger_called_count == 1
        assert distance_value == 500
        assert actual_value == 123.456

        # Change the recorded Ultrasonic value and validate it does not get called
        # a second time.
        ultrasonic.dist = 654.321
        assert trigger.distance == 123.456
        assert ultrasonic.dist_called_count == 1

    def test_adding_single_distance_handler(self) -> None:
        """
        Validates that a handler for a specific distance can be added
        as well as removed without raising an error.
        """
        ultrasonic = TestUltrasonic()
        trigger = UltrasonicTrigger(ultrasonic)
        assert False

    def test_adding_multiple_distance_handlers(self) -> None:
        """
        Validates that handles for different distances can be added
        and specific ones removed without raising an error or removing
        the other distance handlers.
        """
        assert False

    def test_adding_multiple_distance_handlers_for_same_distance(self) -> None:
        """
        Validates that multiple handlers for a specific distance can be added
        and all will be removed with a single action without raising an error.
        """
        assert False

    def test_registering_with_runner(self) -> None:
        """
        Validates the UltrasonicTrigger registers with the Runner.
        """
        add_task_count: int = 0

        class TestRunner(Runner):
            def add_loop_task(self, task: Callable[[], Awaitable[None]]) -> None:
                nonlocal add_task_count
                add_task_count += 1

        runner = TestRunner()
        ultrasonic = TestUltrasonic()
        trigger = UltrasonicTrigger(ultrasonic)
        assert add_task_count == 0
        trigger.register(runner)
        assert add_task_count == 1
