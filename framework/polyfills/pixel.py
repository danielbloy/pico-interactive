from framework.environment import are_pins_available

if are_pins_available():
    from adafruit_led_animation.animation import Animation as Animation
    from adafruit_led_animation.color import BLACK

    from microcontroller import Pin
    from neopixel import NeoPixel as Pixels


    def __new_pixel(pin: Pin, num_pixels: int, brightness: float) -> Pixels:
        pixels: Pixels = Pixels(pin, num_pixels, brightness=brightness, auto_write=False)
        pixels.fill(BLACK)
        pixels.write()
        return pixels


    def __new_animation(pixel_object, speed, color, name=None):
        """This is not expected to be needed but stops PyCharm removing the import"""
        return Animation(pixel_object, speed, color, name)

else:

    class Pixels:
        def __init__(self, pin, num_pixels: int, brightness: float):
            self.pin = pin
            self.num_pixels = num_pixels
            self.brightness = brightness
            self.brightness = brightness

        def deinit(self) -> None:
            pass

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

        def _getitem(self, index):
            return 0

        def __getitem__(self, index):
            return 0


    class Animation:
        """
        Stubs out the Animate class.
        """

        def __init__(self, pixel_object, speed, color, name=None):
            self.pixel_object = pixel_object
            self.speed = speed
            self.color = color
            self.name = name

        def animate(self, show=True):
            pass

        def freeze(self):
            pass

        def resume(self):
            pass

        def fill(self, color):
            self.color = color

        def reset(self):
            pass


    def __new_pixel(pin, num_pixels: int, brightness: float) -> Pixels:
        return Pixels(pin, num_pixels, brightness=brightness)


    def __new_animation(pixel_object, speed, color, name=None):
        """Just for consistency"""
        return Animation(pixel_object, speed, color, name)


def new_pixels(pin, num_pixels: int, brightness: float = 1.0) -> Pixels:
    """
    Returns a new Pixels object that controls a strand of NeoPixels or
    other compatible individually addressable pixel device.

    :param num_pixels: The number of pixels in the strand.
    :param brightness: The brightness of the pixels.
    :param pin: The pin connected to the NeoPixels.
    """
    return __new_pixel(pin, num_pixels, max(min(brightness, 1.0), 0.0))
