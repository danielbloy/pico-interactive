from interactive.environment import are_pins_available

if are_pins_available():

    from adafruit_hcsr04 import HCSR04 as Ultrasonic
    from microcontroller import Pin


    def __new_ultrasonic(trigger: Pin, echo: Pin) -> Ultrasonic:
        return Ultrasonic(trigger_pin=trigger, echo_pin=echo)

else:

    class Ultrasonic:
        def __init__(self, trigger, echo):
            self.trigger = trigger
            self.echo = echo

        @property
        def distance(self) -> float:
            return 0.0


    def __new_ultrasonic(trigger, echo) -> Ultrasonic:
        return Ultrasonic(trigger_pin=trigger, echo_pin=echo)


def new_ultrasonic(trigger, echo) -> Ultrasonic:
    """
    Returns a new HCSR04 compatible sensor that can be used to range
    distances.

    :param trigger: The pin used to trigger the ultrasonic sound.
    :param echo: The pin used to measure the ultrasonic echo.
    """
    return __new_ultrasonic(trigger, echo)
