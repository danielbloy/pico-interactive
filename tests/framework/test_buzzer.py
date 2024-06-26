import pytest

from framework.buzzer import BuzzerController
from framework.polyfills.buzzer import Buzzer


class TestBuzzer(Buzzer):
    def __init__(self):
        super().__init__(None)

        self.update_count = 0

    def update(self) -> None:
        self.update_count += 1


class TestBuzzerController:

    def test_creating_with_none_buzzer_errors(self) -> None:
        """
        Validates that a BuzzerController cannot be constructed with
        a None value.
        """
        with pytest.raises(ValueError):
            BuzzerController(None)

    def test_creating_with_string_errors(self) -> None:
        """
        Validates that a BuzzerController cannot be constructed with
        a value that is not a Buzzer.
        """
        with pytest.raises(ValueError):
            BuzzerController("")
