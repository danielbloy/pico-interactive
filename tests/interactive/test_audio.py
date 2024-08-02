import pytest

from interactive.audio import AudioController


class TestAudio:

    def test_creating_with_none_audio_errors(self) -> None:
        """
        Validates that a AudioController cannot be constructed with
        a None value.
        """
        with pytest.raises(ValueError):
            # noinspection PyTypeChecker
            AudioController(None)

    def test_creating_with_string_errors(self) -> None:
        """
        Validates that a AudioController cannot be constructed with
        a value that is not a Audio.
        """
        with pytest.raises(ValueError):
            # noinspection PyTypeChecker
            AudioController("")

    # TODO: Test that items are added to the queue
    # TODO: Test that items are pulled off the queue o be played.
