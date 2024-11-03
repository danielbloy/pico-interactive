from collections.abc import Callable, Awaitable

import pytest

from interactive.audio import AudioController
from interactive.polyfills.audio import Audio
from interactive.runner import Runner


class MockAudio(Audio):
    def __init__(self):
        super().__init__(None, None)
        self.playing_count = 0
        self.filename = ""
        self.files = []
        self.playing_called = False
        self.paused_called = False
        self.pause_called = False
        self.resume_called = False
        self.stop_called = False

    def play(self, filename: str):
        assert self.playing_count <= 0
        self.files.append(filename)
        self.filename = filename
        self.playing_count += 10

    @property
    def playing(self) -> bool:
        self.playing_called = True
        self.playing_count -= 1
        return self.playing_count > 0

    @playing.setter
    def playing(self, value):
        pass

    @property
    def paused(self) -> bool:
        self.paused_called = True
        return False

    @paused.setter
    def paused(self, value):
        pass

    def pause(self):
        self.pause_called = True

    def resume(self):
        self.resume_called = True

    def stop(self):
        self.stop_called = True


class TestAudioController:

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

    def test_registering_with_runner(self) -> None:
        """
        Validates the AudioController registers with the Runner.
        """
        add_task_count: int = 0

        class TestRunner(Runner):
            def add_loop_task(self, task: Callable[[], Awaitable[None]]) -> None:
                nonlocal add_task_count
                add_task_count += 1

        runner = TestRunner()
        audio = MockAudio()
        controller = AudioController(audio)
        assert add_task_count == 0
        controller.register(runner)
        assert add_task_count == 1

    def test_adding_to_the_queue_gets_picked_up(self) -> None:
        """
        Validates the AudioController picks up a queued song and plays it.
        """
        called_count: int = 0

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= 5

        runner = Runner()
        audio = MockAudio()
        controller = AudioController(audio)
        controller.register(runner)

        # queue a single song.
        controller.queue("track-1.mp3")

        runner.run(callback)
        assert audio.filename == "track-1.mp3"
        assert len(audio.files) == 1
        assert audio.playing_count <= 0
        assert audio.playing_called

    def test_adding_multiple_items_to_the_queue_get_picked_up(self) -> None:
        """
        Validates the AudioController picks up multiple queued songs and
        plays them in order.
        """
        called_count: int = 0

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= 10

        runner = Runner()
        audio = MockAudio()
        controller = AudioController(audio)
        controller.register(runner)

        # queue three songs.
        controller.queue("track-1.mp3")
        controller.queue("track-2.mp3")
        controller.queue("track-3.mp3")

        runner.run(callback)
        assert audio.filename == "track-3.mp3"
        assert len(audio.files) == 3
        assert audio.files[0] == "track-1.mp3"
        assert audio.files[1] == "track-2.mp3"
        assert audio.files[2] == "track-3.mp3"
        assert audio.playing_count <= 0
        assert audio.playing_called

    def test_controls_are_called_correctly(self) -> None:
        """
        Validates the AudioController correctly passes on controls such
        as pause, resume and stopped to Audio.
        """
        called_count: int = 0

        async def callback():
            nonlocal called_count
            called_count += 1
            runner.cancel = called_count >= 5

        runner = Runner()
        audio = MockAudio()
        controller = AudioController(audio)
        controller.register(runner)

        # queue three songs.
        controller.queue("track-1.mp3")
        controller.queue("track-2.mp3")
        controller.queue("track-3.mp3")

        assert not controller.playing
        assert audio.playing_called
        audio.playing_called = False

        assert not controller.paused
        assert audio.paused_called
        audio.paused_called = False

        assert not controller.pause()
        assert audio.pause_called
        audio.pause_called = False

        assert not controller.resume()
        assert audio.resume_called
        audio.resume_called = False

        assert not controller.stop()
        assert audio.stop_called
        audio.stop_called = False

        # Validate cancel stops anything playing and emptys the queue
        assert not controller.cancel()
        assert audio.stop_called
        audio.stop_called = False

        runner.run(callback)
        assert len(audio.files) == 0
        assert audio.playing_count <= 0
