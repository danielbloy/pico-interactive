from interactive.environment import are_pins_available

if are_pins_available():

    from audiomp3 import MP3Decoder
    from microcontroller import Pin

    try:
        from audioio import AudioOut
    except ImportError:
        try:
            from audiopwmio import PWMAudioOut as AudioOut
        except ImportError:
            pass  # not always supported by every board!


    class Audio:

        def __init__(self, pin: Pin, decoder):
            self.audio = AudioOut(pin)
            self.decoder = decoder

        def play(self, filename: str):
            if filename is None or len(filename) <= 0:
                raise ValueError("filename must be specified")

            self.decoder.file = open(filename, "rb")
            self.audio.play(self.decoder)

        @property
        def playing(self) -> bool:
            return self.audio.playing

        @property
        def paused(self) -> bool:
            return self.audio.paused

        def pause(self):
            return self.audio.pause()

        def resume(self):
            return self.audio.resume()

        def stop(self):
            return self.audio.stop()


    def __new_mp3_decoder(file: str) -> MP3Decoder:
        # You have to specify some mp3 file when creating the decoder
        decoder = MP3Decoder(open(file, "rb"))
        return decoder


    def __new_audio(pin: Pin, decoder) -> Audio:
        return Audio(pin, decoder)

else:

    class MP3Decoder:
        def __init__(self, file):
            self.file = file


    class Audio:

        def __init__(self, pin, decoder):
            self.pin = pin
            self.decoder = decoder
            self.filename = None
            self.playing = False
            self.paused = False

        def play(self, filename: str):
            self.filename = filename
            self.playing = True
            self.paused = False

        def pause(self):
            self.playing = False
            self.paused = True

        def resume(self):
            self.playing = True
            self.paused = False

        def stop(self):
            self.playing = False
            self.paused = False


    def __new_mp3_decoder(file: str) -> MP3Decoder:
        return MP3Decoder(file)


    def __new_audio(pin, decoder) -> Audio:
        return Audio(pin, decoder)


def new_mp3_player(pin, file) -> Audio:
    decoder = __new_mp3_decoder(file)
    return __new_audio(pin, decoder)
