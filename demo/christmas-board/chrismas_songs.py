# This file contains some example Christmas songs already prepared using
# the song notation defined in songs.py.

JINGLE_BELLS_MUSIC = [
    "E4:2", "E:2", "E:4", "E:2", "E:2", "E:4",
    "E:2", "G:2", "C:2", "D:2", "E:8",
    "F:2", "F:2", "F:2", "F:2", "F:2", "E:2", "E:2", "E:1", "E:1",
    "E:2", "D:2", "D:2", "E:2", "D:4", "G:2", "R:2",
    "E:2", "E:2", "E:4", "E:2", "E:2", "E:4",
    "E:2", "G:2", "C:2", "D:2", "E:8",
    "F:2", "F:2", "F:2", "F:2", "F:2", "E:2", "E:2", "E:1", "E:1",
    "G:2", "G:2", "F:2", "D:2", "C:8",
    "R:8"]
JINGLE_BELLS_SPEED = 0.1
JINGLE_BELLS = (JINGLE_BELLS_MUSIC, JINGLE_BELLS_SPEED)

RUDOLPH_MUSIC = [
    "G4:1", "A:2", "G:1", "E:2", "C5:2", "A4:2", "G:6",
    "G:1", "A:1", "G:1", "A:1", "G:2", "C5:2", "B4:8",
    "F:1", "G:2", "F:1", "D:2", "B:2", "A:2", "G:6",
    "G:1", "A:1", "G:1", "A:1", "G:2", "A:2", "E:8",
    "G:1", "A:2", "G:1", "E:2", "C5:2", "A4:2", "G:6",
    "G:1", "A:1", "G:1", "A:1", "G:2", "C5:2", "B4:8",

    "F:1", "G:2", "F:1", "D:2", "B:2", "A:2", "G:6",
    "G:1", "A:1", "G:1", "A:1", "G:2", "D5:2", "C:8",
    "A4:2", "A:2", "C5:2", "A4:2", "G:2", "E:2", "G:4",
    "F:2", "A:2", "G:2", "F:2", "E:8",
    "D:2", "E:2", "G:2", "A:2", "B:2", "B:2", "B:4",
    "D5:2", "C:2", "B4:2", "A:2", "G:2", "F:2", "D:4",

    "G:1", "A:2", "G:1", "E:2", "C5:2", "A4:2", "G:6",
    "G:1", "A:1", "G:1", "A:1", "G:2", "C5:2", "B4:8",
    "F:1", "G:2", "F:1", "D:2", "B:2", "A:2", "G:6",
    "G:1", "A:1", "G:1", "A:1", "G:2", "D5:2", "C:8",
    "R:8"]
RUDOLPH_SPEED = 0.15
RUDOLPH = (RUDOLPH_MUSIC, RUDOLPH_SPEED)

SANTA_MUSIC = [
    "G4:1",
    "C:1", "C:1", "D:1", "E:1", "E:1", "F:1", "G:3", "C5:3",
    "A4:2", "G:1", "F:2", "A:1", "G:3", "R:2", "G:1",

    "C5:2", "C:1", "B4:2", "B:1", "A:1", "A:1", "A:1", "G:2", "G:1",
    "E:2", "E:1", "D:2", "C:1", "G:3", "R:2", "G:1",

    "C5:2", "C:1", "B4:2", "B:1", "A:1", "A:1", "A:1", "G:2", "G:1",
    "E:2", "E:1", "G:1", "F:1", "E:1", "D:3", "R:2", "G:1",

    "C:1", "C:1", "D:1", "E:1", "E:1", "F:1", "G:3", "C5:2", "A4:1",
    "G:2", "C5:1", "B4:2", "D5:1", "C:7",

    "R:8"]
SANTA_SPEED = 0.15
SANTA = (SANTA_MUSIC, SANTA_SPEED)

MERRY_CHRISTMAS_MUSIC = [
    "D4:2",
    "G:2", "G:1", "A:1", "G:1", "F:1", "E:2", "C:2", "E:2",
    "A:2", "A:1", "B:1", "A:1", "G:1", "F:2", "D:2", "F:2",
    "B:2", "B:1", "C5:1", "B4:1", "A:1", "G:2", "E:2", "D:1", "D:1",
    "E:2", "A:2", "F:2", "G:4", "D:2",
    "G:2", "G:2", "G:2", "F:4", "F:2",
    "G:2", "F:2", "E:2", "D:4", "A:2",
    "B:2", "A:1", "A:1", "G:1", "G:1", "D5:2", "D4:2", "D:1", "D:1",
    "E:2", "A:2", "F:2", "G:4", "R:2",
    "R:4"]
MERRY_CHRISTMAS_SPEED = 0.15
MERRY_CHRISTMAS = (MERRY_CHRISTMAS_MUSIC, MERRY_CHRISTMAS_SPEED)

ALL_SONGS = [JINGLE_BELLS, RUDOLPH, SANTA, MERRY_CHRISTMAS]
