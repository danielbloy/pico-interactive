import digitalio
from microcontroller import Pin
import pwmio

try:
    from typing import Optional, Tuple, Union, Sequence

    ColorUnion = Union[int, Tuple[int, int, int], Tuple[int, int, int, int]]
except ImportError:
    pass

MAX_DUTY = 65535


class LED:
    def __init__(self, pin: Pin, brightness: float = 1.0, auto_write: bool = True):

        if brightness < 0 or brightness > 1.0:
            raise Exception("LEDs: Brightness %s is out of range!" % brightness)

        self.pin = pin
        self.pwm = pwmio.PWMOut(pin, frequency=1000)
        self.auto_write = auto_write

        self._brightness = 1.0
        self.brightness = brightness

    def deinit(self) -> None:
        self.fill(0)
        self.show()
        self.pin.deinit()

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, value: float):
        value = min(max(value, 0.0), 1.0)
        change = value - self._brightness
        if -0.001 < change < 0.001:
            return

        self._brightness = value

        if self.auto_write:
            self.show()

    # Turns the LED fully on.
    def on(self):
        self.brightness = 1.0

    # Turns the LED fully off.
    def off(self):
        self.brightness = 0.0

    @property
    def n(self) -> int:
        return 1

    def __len__(self):
        return 1

    def show(self) -> None:
        self.pwm.duty_cycle = int(MAX_DUTY * self._brightness)

    def fill(self, color: ColorUnion):
        r, g, b, w = self._parse_color(color)
        self.brightness = w / 0xFF
        if self.auto_write:
            self.show()

    @staticmethod
    def _parse_color(value: ColorUnion) -> Tuple[int, int, int, int]:
        # If 4 colours are specified, the 4th colour is used for the LED brightness.
        if isinstance(value, int):
            r = value >> 16
            g = (value >> 8) & 0xFF
            b = value & 0xFF
            # Average out the RBG intensities.
            w = (r + g + b) / 3

        else:
            if len(value) < 3 or len(value) > 4:
                raise ValueError(
                    "Expected tuple of length {}, got {}".format(4, len(value))
                )

            if len(value) == 3:
                r, g, b = value
                # Average out the RBG intensities.
                w = (r + g + b) / 3
            else:
                r, g, b, w = value

        return r, g, b, w

    def __setitem__(self, index: Union[int, slice], val: Union[ColorUnion, Sequence[ColorUnion]]):
        if isinstance(index, slice):
            val = val[0]

        r, g, b, w = self._parse_color(val)
        self.fill((r, g, b, w))

    def __getitem__(self, index: Union[int, slice]):
        val = self.brightness * 255
        return val, val, val
