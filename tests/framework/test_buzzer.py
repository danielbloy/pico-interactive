from collections.abc import Callable, Awaitable

import pytest

from framework.buzzer import BuzzerController
from framework.polyfills.buzzer import Buzzer
from framework.runner import Runner


class TestBuzzer(Buzzer):
    def __init__(self):
        super().__init__(None)

        self.play_count = 0
        self.last_frequency = 0
        self.off_count = 0

    def play(self, frequency: int) -> None:
        self.play_count += 1
        self.last_frequency = frequency

    def off(self) -> None:
        self.off_count += 1


class TestBuzzerController:

    def test_creating_with_none_buzzer_errors(self) -> None:
        """
        Validates that a BuzzerController cannot be constructed with
        a None value.
        """
        with pytest.raises(ValueError):
            # noinspection PyTypeChecker
            BuzzerController(None)

    def test_creating_with_string_errors(self) -> None:
        """
        Validates that a BuzzerController cannot be constructed with
        a value that is not a Buzzer.
        """
        with pytest.raises(ValueError):
            # noinspection PyTypeChecker
            BuzzerController("")

    def test_registering_with_runner(self) -> None:
        """
        Validates the BuzzerController registers with the Runner.
        """
        add_task_count: int = 0

        class TestRunner(Runner):
            def add_loop_task(self, task: Callable[[], Awaitable[None]]) -> None:
                nonlocal add_task_count
                add_task_count += 1

        runner = TestRunner()
        button = TestBuzzer()
        controller = BuzzerController(button)
        assert add_task_count == 0
        controller.register(runner)
        assert add_task_count == 1

    def test_play(self) -> None:
        assert False

    def test_off_gets_called_automatically_after_play(self) -> None:
        assert False

    def test_beep(self) -> None:
        assert False

    def test_beeps(self) -> None:
        assert False

    def test_off(self) -> None:
        assert False
