from interactive.environment import are_pins_available

if are_pins_available():

    import board

    from audiomp3 import MP3Decoder
    from microcontroller import Pin

    try:
        from audioio import AudioOut
    except ImportError:
        try:
            from audiopwmio import PWMAudioOut as AudioOut
        except ImportError:
            pass  # not always supported by every board!

        audio = AudioOut(board.A0)


    class Audio(AudioOut):
        pass


    def __new_mp3_decoder(file: str) -> MP3Decoder:
        # You have to specify some mp3 file when creating the decoder
        mp3 = open(file, "rb")
        decoder = MP3Decoder(mp3)
        return decoder


    def __new_audio(pin: Pin, decoder: Decoder) -> Audio:
        return Audio(pin, decoder)

else:

    class MP3Decoder:
        def __init__(self):
            self.file = ""


    class Audio:
        pass


    def __new_mp3_decoder(file: str) -> MP3Decoder:
        return MP3Decoder()


    def __new_audio(pin, decoder) -> Audio:
        return Audio(pin, decoder)


def new_mp3_player(pin, file) -> Audio:
    decoder = __new_mp3_decoder(file)
    return __new_audio(pin, decoder)
