# Support for HC-SR04 ultrasonic sensor in CircuitPython:
#   * https://learn.adafruit.com/ultrasonic-sonar-distance-sensors/python-circuitpython
#   * https://github.com/adafruit/Adafruit_CircuitPython_HCSR04

from interactive.environment import are_pins_available

ULTRASONIC_MIN_DISTANCE = 10
ULTRASONIC_MAX_DISTANCE = 600

if are_pins_available():

    from adafruit_hcsr04 import HCSR04
    from microcontroller import Pin


    class Ultrasonic(HCSR04):

        @property
        def distance(self) -> float:
            """Return the distance measured by the sensor in cm or the maximum
            distance (600 cm) if nothing is detected. If the distance detected
            is less than the minimum amount then the minimum amount is returned.

            :return: Distance in centimeters.
            :rtype: float
            """
            try:
                distance = self._dist_two_wire()
                if distance < ULTRASONIC_MIN_DISTANCE:
                    distance = ULTRASONIC_MIN_DISTANCE
                return distance
            except RuntimeError:
                return ULTRASONIC_MAX_DISTANCE


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
        return Ultrasonic(trigger=trigger, echo=echo)


def new_ultrasonic(trigger, echo) -> Ultrasonic:
    """
    Returns a new HCSR04 compatible sensor that can be used to range
    distances.

    :param trigger: The pin used to trigger the ultrasonic sound.
    :param echo: The pin used to measure the ultrasonic echo.
    """
    return __new_ultrasonic(trigger, echo)
