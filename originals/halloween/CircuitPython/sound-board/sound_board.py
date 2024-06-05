import board
import digitalio

from audiomp3 import MP3Decoder

# The pins determine which sound to play
buttons = [
    digitalio.DigitalInOut(board.GP14),
    digitalio.DigitalInOut(board.GP13),
    digitalio.DigitalInOut(board.GP12),
    digitalio.DigitalInOut(board.GP11),
    digitalio.DigitalInOut(board.GP10),
    digitalio.DigitalInOut(board.GP9)
]

buttons_state = [
    False,
    False,
    False,
    False,
    False,
    False
]

# Set all buttons to be pull down as we want the signals to be driven by
# other microcontrollers as well as buttons. Cancel doesn't need a state
# as pressing it simply cancels everything all the time.
for button in buttons:
    button.switch_to_input(pull=digitalio.Pull.DOWN)

# A cancel button to stop sound.
cancel = digitalio.DigitalInOut(board.GP15)
cancel.switch_to_input(pull=digitalio.Pull.DOWN)

try:
    from audioio import AudioOut
except ImportError:
    try:
        from audiopwmio import PWMAudioOut as AudioOut
    except ImportError:
        pass  # not always supported by every board!

# The listed mp3files will be played in order
mp3files = {0: "", 1: "", 2: "", 3: "", 4: "", 5: ""}

decoder = None
audio = None


def play(filename):
    if len(filename) <= 0:
        return

    # Updating the .file property of the existing decoder
    # helps avoid running out of memory (MemoryError exception)
    decoder.file = open(filename, "rb")
    audio.play(decoder)


def run():
    global decoder, audio

    # You have to specify some mp3 file when creating the decoder
    mp3 = open(mp3files[0], "rb")
    decoder = MP3Decoder(mp3)
    audio = AudioOut(board.A0)

    # In this loop, we listen for button presses. When detected, we queue up the
    # relevant sound to be played. The sounds will be played in the order that
    # they are triggered. If a cancel button is pressed, the entire queue is cleared.
    queue = []
    while True:
        # Test for the cancel button and clear the queue.
        if cancel.value:
            queue.clear()
            audio.stop()

        # Test each button and queue up the appropriate sound
        for index, button in enumerate(buttons):
            if button.value != buttons_state[index]:
                # Play on button release.
                if not button.value:
                    queue.append(mp3files[index])
                buttons_state[index] = button.value

        # If there is no audio playing and a song queued up then play.
        if not audio.playing and len(queue) > 0:
            song = queue.pop(0)
            play(song)
