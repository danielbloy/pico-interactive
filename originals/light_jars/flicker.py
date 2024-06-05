from environment import isBlinkaAvailable

if isBlinkaAvailable:

    import array
    import random
    from adafruit_led_animation.animation import Animation


    class Flicker(Animation):
        """
        This flickers each neopixel that is "on" (has a brightness > 0). This function
        by default flickers each pixel but is configurable using every. The flicker
        sets the brightness of the pixels to a random value between base and (base + flame).
        """

        def __init__(
                self, pixel_object, speed, color, spacing=1, base=150, flame=105, name=None):
            size = len(pixel_object)
            self._size = size
            self._spacing = spacing
            self._base = base
            self._flame = flame
            self._red = array.array("I", [0 for _ in range(size)])
            self._green = array.array("I", [0 for _ in range(size)])
            self._blue = array.array("I", [0 for _ in range(size)])
            super().__init__(pixel_object, speed, color, name=name)
            self.set_all(color)

        def get(self, i):
            if i < 0 or i >= self._size:
                raise Exception("NeoPixels: Index %s is out of bounds!" % i)

            r = int(self._red[i]) & 0xFF  # 8-bit red dimmed to brightness
            g = int(self._green[i]) & 0xFF  # 8-bit green dimmed to brightness
            b = int(self._blue[i]) & 0xFF  # 8-bit blue dimmed to brightness
            return r, g, b

        def set(self, i, colour):
            if i < 0 or i >= self._size:
                raise Exception("NeoPixels: Index %s is out of bounds!" % i)

            self._red[i] = colour[0] & 0xFF
            self._green[i] = colour[1] & 0xFF
            self._blue[i] = colour[2] & 0xFF
            self.pixel_object[i] = (self._red[i], self._green[i], self._blue[i])

        def set_all(self, colour):
            for i in range(self._size):
                self.set(i, colour)  # show all colors

        def draw(self):
            for i in range(0, self._size, self._spacing):
                brightness = random.randint(0, self._flame)
                r = int(self._red[i] * (self._base + brightness) / 255) & 0xFF  # 8-bit red dimmed to brightness
                g = int(self._green[i] * (self._base + brightness) / 255) & 0xFF  # 8-bit green dimmed to brightness
                b = int(self._blue[i] * (self._base + brightness) / 255) & 0xFF  # 8-bit blue dimmed to brightness
                self.pixel_object[i] = (r, g, b)

        def __len__(self):
            """
            Number of pixels.
            """
            return self._size

        def __getitem__(self, index: int):
            return self.get(index)

        def __setitem__(self, index: int, colour):
            self.set(index, colour)
