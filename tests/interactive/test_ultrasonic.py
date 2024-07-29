from collections.abc import Callable, Awaitable

import pytest

from interactive.polyfills.ultrasonic import Ultrasonic
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

        assert False

    def test_distance_returns_last_sensor_Value(self) -> None:
        """
        Validates that the distance property returns the last distance value
        returned from the Ultrasonic sensor and does not sample it when
        called.
        """

        assert False

    def test_adding_single_distance_handler(self) -> None:
        """
        Validates that a handler for a specific distance can be added
        as well as removed without raising an error.
        """
        assert False

    def test_adding_multiple_distance_handlers(self) -> None:
        """
        Validates that handles for different distances can be added
        and specifiec ones removed without raising an error or removing
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
