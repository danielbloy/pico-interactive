import time

from framework.control import NS_PER_SECOND
from framework.polyfills.buzzer import Buzzer
from framework.runner import Runner


class BuzzerController:

    def __init__(self, buzzer: Buzzer):
        if buzzer is None:
            raise ValueError("buzzer cannot be None")

        if not isinstance(buzzer, Buzzer):
            raise ValueError("buzzer must be of type Buzzer")

        self.__buzzer = buzzer
        self.__playing = False
        self.__stop_time_ns = 0
        self.__beeps = 0

    def beep(self) -> None:
        """
        Makes a beep.
        """
        self.__beeps -= 1
        self.play(262, 0.5)

    def beeps(self, count: int) -> None:
        """
        Plays a series of beeps.

        :param count: The number of beeps to play.
        """
        self.__beeps = count
        self.beep()

    def play(self, frequency: int, duration: float) -> None:
        """
        Plays a tone at the given frequency for the specified number of seconds.

        :param frequency: The frequency to play the tone at.
        :param duration: The duration in seconds to play the tone for.
        """
        # Calculate the stop time.
        self.__stop_time_ns = time.monotonic_ns() + int(duration * NS_PER_SECOND)
        self.__playing = True
        self.__buzzer.play(frequency)

    def off(self) -> None:
        """
        Turns off the buzzer.
        """
        self.__playing = False
        self.__buzzer.off()

    def register(self, runner: Runner) -> None:
        """
        Registers this Buzzer instance as a task with the provided Runner.

        :param runner: the runner to register with.
        """
        runner.add_loop_task(self.__loop)

    async def __loop(self):
        """
        Internal loop to turn the buzzer off at the desired time internal.
        """
        if (self.__playing or self.__beeps > 0) and time.monotonic_ns() >= self.__stop_time_ns:
            if self.__playing:
                self.off()

                # Allow for a delay between beeps.
                if self.__beeps > 0:
                    self.__stop_time_ns += (0.2 * NS_PER_SECOND)

            else:

                # If there are more beeps expected in the sequence then play them.
                if self.__beeps > 0:
                    self.beep()


# TODO: Comment this class
# TODO: Write tests for this class.
# TODO: Write new MelodyController to easily attach Melody to a runner.
class Melody:
    def __init__(self, buzzer: Buzzer, song: [(int, int)], speed, loop=True, paused=False, name=None):

        self._buzzer = buzzer
        self._song = song
        self._index = 0  # The next note to play.
        self._loop = loop
        self._paused = paused
        self._speed_ns = 0
        self._next_update = time.monotonic_ns()
        self._time_left_at_pause = 0
        self.speed = speed  # sets _speed_ns
        self.name = name

    def play(self) -> bool:
        if self.paused:
            return False

        now = time.monotonic_ns()
        if now < self._next_update:
            return False

        frequency, duration = self._song[self._index]
        self._index += 1
        if self._index >= len(self._song):
            self._index = 0
            if not self._loop:
                self.pause()

        self._buzzer.play(frequency)

        self._next_update = now + (self._speed_ns * duration)
        return True

    @property
    def paused(self) -> bool:
        return self._paused

    def pause(self):
        """
        Stops playing until resumed.
        """
        if self.paused:
            return

        self._paused = True
        self._time_left_at_pause = max(0, time.monotonic_ns() - self._next_update)

        self._buzzer.off()

    def resume(self) -> None:
        """
        Resumes the music if it has been paused.
        """
        if not self.paused:
            return

        self._next_update = time.monotonic_ns() + self._time_left_at_pause
        self._time_left_at_pause = 0
        self._paused = False

        frequency, duration = 0, 0
        if self._index > 0:
            frequency, duration = self._song[self._index]

        self._buzzer.play(frequency)

    @property
    def speed(self) -> float:
        """
        The speed in fractional seconds.
        """
        return self._speed_ns / NS_PER_SECOND

    @speed.setter
    def speed(self, seconds) -> None:
        self._speed_ns = int(seconds * NS_PER_SECOND)

    def reset(self) -> None:
        """
        Resets the music sequence back to the beginning.
        """
        self._buzzer.off()
        self._index = 0


# TODO: Comment this class
# TODO: Write tests for this class.
class MelodySequence:
    def __init__(self, *members: Melody, loop=True, name=None):
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
        Activates a specific melody.
        """
        self.melody.reset()
        self.melody.resume()
        if isinstance(index, str):
            self._current = [member.name for member in self._members].index(index)
        else:
            self._current = index

        self.melody.reset()
        self.melody.resume()

    def next(self):
        """
        Jump to the next melody.
        """
        current = self._current + 1
        if current >= len(self._members):
            if not self._loop:
                self.pause()

        self.activate(current % len(self._members))

    def previous(self):
        """
        Jump to the previous melody.
        """
        current = self._current - 1
        self.activate(current % len(self._members))

    def play(self):
        """
        Plays the current melody or goes to the next melody.
        """
        if not self.paused and self.melody.paused:
            self.next()

        if not self.paused:
            return self.melody.play()

        return False

    @property
    def melody(self) -> Melody:
        """
        Returns the current melody in the sequence.
        """
        return self._members[self._current]

    @property
    def paused(self):
        return self._paused

    def pause(self):
        """
        Pauses the current melody in the sequence.
        """
        if self.paused:
            return
        self._paused = True
        self.melody.pause()

    def resume(self):
        """
        Resume the current melody in the sequence, and resumes auto advance if enabled.
        """
        if not self.paused:
            return
        self._paused = False
        self.melody.resume()

    def reset(self):
        """
        Resets the current melody to the first song.
        """
        self.activate(0)


# Coverts an encoded note to a tuple of (note, octave, duration)
# The encoded note can be one of:
#   <note>:<duration>
#   <note><octave>:<duration>
#
# Examples:
#    C:1
#    A5:2
#
# TODO: Comment and test
def parse_encoded_note(encoded_note: str) -> (str, int, int):
    # -1 means use the same octave as the previous note.
    octave = -1

    parts = encoded_note.split(":")
    # The first character of the first part is the note.
    note = parts[0][0]

    # If the first part has a second character, use it as the octave.
    if len(parts[0]) > 1:
        octave = int(parts[0][1])

    # The second part is the duration as an integer number.
    duration = int(parts[1])

    return note, octave, duration


# Converts the song into a list of tuples of: (note, octave, duration)
# TODO: Comment and test
def encoded_song_to_triplets(song: [str]) -> [(str, int, int)]:
    result = []

    current_octave = 4

    for encoded_note in song:
        note, octave, duration = parse_encoded_note(encoded_note)
        if octave < 0:
            octave = current_octave
        else:
            current_octave = octave

        # Rests should always have a zero octave.
        if note == "P" or note == "R":
            note = "P"
            octave = 0

        result.append((note, octave, duration))

    return result


# Converts a song of (note, octave, duration) triplets to (tone, duration) pairs.
# TODO: Comment and test.
def triplets_to_tones_and_durations(song: [(str, int, int)]) -> [(int, int)]:
    result = []
    for note, octave, duration in song:
        tone = note + str(octave)
        result.append((TONES[tone], duration))

    return result


# Coverts a song of encoded notes into pairs of (tone, duration).
# TODO: Comment and test.
def decode_song(encoded_song: [str]) -> [(int, int)]:
    return triplets_to_tones_and_durations(encoded_song_to_triplets(encoded_song))


TONES = {
    "P0": 0,
    "B0": 31,
    "C1": 33,
    "CS1": 35,
    "D1": 37,
    "DS1": 39,
    "E1": 41,
    "F1": 44,
    "FS1": 46,
    "G1": 49,
    "GS1": 52,
    "A1": 55,
    "AS1": 58,
    "B1": 62,
    "C2": 65,
    "CS2": 69,
    "D2": 73,
    "DS2": 78,
    "E2": 82,
    "F2": 87,
    "FS2": 93,
    "G2": 98,
    "GS2": 104,
    "A2": 110,
    "AS2": 117,
    "B2": 123,
    "C3": 131,
    "CS3": 139,
    "D3": 147,
    "DS3": 156,
    "E3": 165,
    "F3": 175,
    "FS3": 185,
    "G3": 196,
    "GS3": 208,
    "A3": 220,
    "AS3": 233,
    "B3": 247,
    "C4": 262,
    "CS4": 277,
    "D4": 294,
    "DS4": 311,
    "E4": 330,
    "F4": 349,
    "FS4": 370,
    "G4": 392,
    "GS4": 415,
    "A4": 440,
    "AS4": 466,
    "B4": 494,
    "C5": 523,
    "CS5": 554,
    "D5": 587,
    "DS5": 622,
    "E5": 659,
    "F5": 698,
    "FS5": 740,
    "G5": 784,
    "GS5": 831,
    "A5": 880,
    "AS5": 932,
    "B5": 988,
    "C6": 1047,
    "CS6": 1109,
    "D6": 1175,
    "DS6": 1245,
    "E6": 1319,
    "F6": 1397,
    "FS6": 1480,
    "G6": 1568,
    "GS6": 1661,
    "A6": 1760,
    "AS6": 1865,
    "B6": 1976,
    "C7": 2093,
    "CS7": 2217,
    "D7": 2349,
    "DS7": 2489,
    "E7": 2637,
    "F7": 2794,
    "FS7": 2960,
    "G7": 3136,
    "GS7": 3322,
    "A7": 3520,
    "AS7": 3729,
    "B7": 3951,
    "C8": 4186,
    "CS8": 4435,
    "D8": 4699,
    "DS8": 4978
}
