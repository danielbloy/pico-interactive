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

    # TODO: Check that distance does not sample.
    ## TODO: Check that distance has a max default.

    # TODO: Test adding and removing trigger events
    # TODO: Check decay

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
