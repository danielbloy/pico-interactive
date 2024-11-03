from interactive.environment import are_pins_available

if are_pins_available():
    from adafruit_led_animation.color import BLACK

    from microcontroller import Pin
    from neopixel import NeoPixel as Pixels


    def __new_pixel(pin: Pin, num_pixels: int, brightness: float) -> Pixels:
        pixels: Pixels = Pixels(pin, num_pixels, brightness=brightness, auto_write=False)
        pixels.fill(BLACK)
        pixels.write()
        return pixels

else:

    class Pixels:
        def __init__(self, pin, num_pixels: int, brightness: float):
            self.pin = pin
            self.num_pixels = num_pixels
            self.brightness = brightness

        def deinit(self) -> None:
            pass

        def __len__(self):
            return self.num_pixels

        @property
        def n(self) -> int:
            return self.num_pixels

        def write(self) -> None:
            pass

        def show(self):
            pass

        def fill(self, color):
            pass

        def _set_item(self, index: int, r: int, g: int, b: int, w: int):
            pass

        def __setitem__(self, index, val):
            pass

        # noinspection PyMethodMayBeStatic
        def _getitem(self, index):
            return index

        def __getitem__(self, index):
            return 0


    def __new_pixel(pin, num_pixels: int, brightness: float) -> Pixels:
        return Pixels(pin, num_pixels, brightness=brightness)


def new_pixels(pin, num_pixels: int, brightness: float = 1.0) -> Pixels:
    """
    Returns a new Pixels object that controls a strand of NeoPixels or
    other compatible individually addressable pixel device.

    :param num_pixels: The number of pixels in the strand.
    :param brightness: The brightness of the pixels.
    :param pin: The pin connected to the NeoPixels.
    """
    return __new_pixel(pin, num_pixels, max(min(brightness, 1.0), 0.0))
