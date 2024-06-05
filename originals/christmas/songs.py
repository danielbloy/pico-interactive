# Coverts an encoded note to a tuple of (note, octave, duration)
# The encoded note can be one of:
#   <note>:<duration>
#   <note><octave>:<duration>
#
# Examples:
#    C:1
#    A5:2
#
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
def triplets_to_tones_and_durations(song: [(str, int, int)]) -> [(int, int)]:
    result = []
    for note, octave, duration in song:
        tone = note + str(octave)
        result.append((TONES[tone], duration))

    return result


# Coverts a song of encoded notes into pairs of (tone, duration).
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
