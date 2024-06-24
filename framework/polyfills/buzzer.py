from framework.environment import are_pins_available

if are_pins_available():

    from microcontroller import Pin


    def __new_button(pin: Pin) -> Buzzer:
        pass

else:
    class Buzzer:
        """
        TODO: Implement a Buzzer that works on a desktop.
        """

        def __init__(self, pin):
            pass

        def update(self) -> None:
            pass


    def __new_buzzer(pin) -> Buzzer:
        return Buzzer(pin)


def new_buzzer(pin) -> Buzzer:
    """
    Returns a new Buzzer that perform the buzzer processing based on
    whether the code is running in CircuitPython where a pin will be
    provided or in a desktop environment where a key will be used.

    :param pin: The pin or key to use for the button signal.
    """
    return __new_buzzer(pin)
