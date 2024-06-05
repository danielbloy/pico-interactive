import pwmio
from microcontroller import Pin

from adafruit_led_animation import MS_PER_SECOND, monotonic_ms


class AudioPin:
    def __init__(self, pin: Pin, volume=2 ** 10):
        self._pin = pin
        self._buzzer = None
        self._volume = volume

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, volume):
        self._volume = volume

    def play(self, frequency: int):
        if self._buzzer:
            self._buzzer.deinit()
            self._buzzer = None

        if frequency == 0:
            self.off()
        else:
            self._buzzer = pwmio.PWMOut(self._pin, frequency=frequency)
            self._buzzer.duty_cycle = self.volume

    def off(self):
        if self._buzzer:
            if self._buzzer is not None:
                self._buzzer.duty_cycle = 0
                self._buzzer.deinit()
            self._buzzer = None


class Song:
    def __init__(self, pin: AudioPin, song: [(int, int)], speed, loop=True, paused=False, name=None):

        self._pin = pin
        self._song = song
        self._index = 0  # The next note to play.
        self._loop = loop
        self._paused = paused
        self._speed_ms = 0
        self._next_update = monotonic_ms()
        self._time_left_at_pause = 0
        self.speed = speed  # sets _speed_ms
        self.name = name

    def play(self):
        if self.paused:
            return False

        now = monotonic_ms()
        if now < self._next_update:
            return False

        frequency, duration = self._song[self._index]
        self._index += 1
        if self._index >= len(self._song):
            self._index = 0
            if not self._loop:
                self.pause()

        self._pin.play(frequency)

        self._next_update = now + (self._speed_ms * duration)
        return True

    @property
    def paused(self):
        return self._paused

    def pause(self):
        """
        Stops playing until resumed.
        """
        if self.paused:
            return

        self._paused = True
        self._time_left_at_pause = max(0, monotonic_ms() - self._next_update)

        self._pin.off()

    def resume(self):
        """
        Resumes the music if it has been paused.
        """
        if not self.paused:
            return

        self._next_update = monotonic_ms() + self._time_left_at_pause
        self._time_left_at_pause = 0
        self._paused = False

        frequency, duration = 0, 0
        if self._index > 0:
            frequency, duration = self._song[self._index]

        self._pin.play(frequency)

    @property
    def speed(self):
        """
        The speed in fractional seconds.
        """
        return self._speed_ms / MS_PER_SECOND

    @speed.setter
    def speed(self, seconds):
        self._speed_ms = int(seconds * MS_PER_SECOND)

    def reset(self):
        """
        Resets the music sequence back to the beginning.
        """
        self._pin.off()
        self._index = 0


class SongSequence:
    def __init__(self, *members: Song, loop=True, name=None):
        self._members = members
        self._loop = loop
        self._current = 0
        self._paused = False
        self.name = name
        # Disable auto loop in the individual songs.
        for member in self._members:
            member._loop = False

    def activate(self, index):
        """
        Activates a specific song.
        """
        self.song.reset()
        self.song.resume()
        if isinstance(index, str):
            self._current = [member.name for member in self._members].index(index)
        else:
            self._current = index

        self.song.reset()
        self.song.resume()

    def next(self):
        """
        Jump to the next song.
        """
        current = self._current + 1
        if current >= len(self._members):
            if not self._loop:
                self.pause()

        self.activate(current % len(self._members))

    def previous(self):
        """
        Jump to the previous song.
        """
        current = self._current - 1
        self.activate(current % len(self._members))

    def play(self):
        """
        Call play() from your code's main loop. It will play the current song
        or go to the next song.
        """
        if not self.paused and self.song.paused:
            self.next()

        if not self.paused:
            return self.song.play()

        return False

    @property
    def song(self) -> Song:
        """
        Returns the current song in the sequence.
        """
        return self._members[self._current]

    @property
    def paused(self):
        return self._paused

    def pause(self):
        """
        Pauses the current song in the sequence.
        """
        if self.paused:
            return
        self._paused = True
        self.song.pause()

    def resume(self):
        """
        Resume the current song in the sequence, and resumes auto advance if enabled.
        """
        if not self.paused:
            return
        self._paused = False
        self.song.resume()

    def reset(self):
        """
        Resets the current song to the first song.
        """
        self.activate(0)
