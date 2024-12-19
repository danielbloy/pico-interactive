from interactive.environment import are_pins_available


class Microphone:
    """

    TODO: Have a callback when each quantised value is returned
    TODO: Record()
    TODO: recording
    TODO: Pause()
    TODO: Paused
    TODO: Resume()
    TODO: Stop()
    # TODO: Should this create a subtask when playing or use the update method.

    Stub implementation of Microphone for Desktop without pins. Does nothing.
    """

    def __init__(self, pin, sample_rate: int):
        pass


if are_pins_available():

    from microcontroller import Pin


    def __new_microphone(pin: Pin, sample_rate) -> Microphone:
        """
        Sets up a basic microphone that receives a simple analogue value from an input pin.
        This is typical of a MAX4466 type device.

        :param pin: The pin to use for the microphone signal.
        """
        return Microphone(pin, sample_rate)

else:

    def __new_microphone(pin, sample_rate) -> Button:
        return Microphone(pin, sample_rate)


def new_microphone(pin, sample_rate) -> Microphone:
    """
    Returns a new Microphone that performs the microphone processing based on
    whether the code is running in CircuitPython where a pin will be provided
    or in a desktop environment where nothing will be done.

    :param pin: The pin to use for the microphone signal.
    :param sample_rate: The number of samples per second.
    """
    return __new_microphone(pin, sample_rate)
