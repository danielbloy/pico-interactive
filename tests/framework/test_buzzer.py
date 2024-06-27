import time
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
        buzzer = TestBuzzer()
        controller = BuzzerController(buzzer)
        assert add_task_count == 0
        controller.register(runner)
        assert add_task_count == 1

    def test_play(self) -> None:
        """
        Validates play invokes the buzzer with the correct values.
        """
        buzzer = TestBuzzer()
        controller = BuzzerController(buzzer)
        controller.play(999, 32.5)

        assert buzzer.last_frequency == 999
        assert buzzer.play_count == 1
        assert buzzer.off_count == 0

    def test_off(self) -> None:
        """
        Validates off invokes the buzzer with the correct values.
        """
        buzzer = TestBuzzer()
        controller = BuzzerController(buzzer)
        controller.play(999, 32.5)

        assert buzzer.last_frequency == 999
        assert buzzer.play_count == 1

        controller.off()

        assert buzzer.last_frequency == 999
        assert buzzer.play_count == 1
        assert buzzer.off_count == 1

    def test_beep(self) -> None:
        """
        Validates beep() invokes the buzzer with default values.
        """
        buzzer = TestBuzzer()
        controller = BuzzerController(buzzer)
        controller.beep()

        assert buzzer.last_frequency > 200
        assert buzzer.play_count == 1

    def test_off_gets_called_automatically_after_play(self) -> None:
        """
        Validates that off gets called automatically after the buzzer has
        buzzed for long enough.
        """

        async def callback():
            nonlocal start, finish
            runner.cancel = time.monotonic() > finish
            assert buzzer.last_frequency == 999
            assert buzzer.play_count == 1

            if runner.cancel:
                assert buzzer.off_count == 1
            else:
                assert buzzer.off_count == 0

        runner = Runner()
        buzzer = TestBuzzer()
        controller = BuzzerController(buzzer)
        controller.register(runner)
        controller.play(999, 0.2)

        # Calling play will starts the buzzer, it will only
        # get turned off at the appropriate time.
        assert buzzer.last_frequency == 999
        assert buzzer.play_count == 1
        assert buzzer.off_count == 0

        start = time.monotonic()
        finish = start + 0.2
        runner.run(callback)

        assert buzzer.last_frequency == 999
        assert buzzer.play_count == 1
        assert buzzer.off_count == 1

    def test_beeps(self) -> None:
        """
        Validates beeps() invokes the buzzer multiple times.
        """

        async def callback():
            nonlocal start, finish
            runner.cancel = time.monotonic() > finish

        runner = Runner()
        buzzer = TestBuzzer()
        controller = BuzzerController(buzzer)
        controller.register(runner)
        controller.beeps(3)

        # Calling play will starts the buzzer, it will only
        # get turned off at the appropriate time.
        assert buzzer.last_frequency == 262
        assert buzzer.play_count == 1
        assert buzzer.off_count == 0

        start = time.monotonic()
        finish = start + 2
        runner.run(callback)

        assert buzzer.last_frequency == 262
        assert buzzer.play_count == 3
        assert buzzer.off_count == 3
