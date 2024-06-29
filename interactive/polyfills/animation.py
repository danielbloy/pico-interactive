from interactive.environment import are_pins_available

if are_pins_available():
    from adafruit_led_animation.animation import Animation as Animation


    def __new_animation(pixel_object, speed, color, name=None):
        """This is not expected to be needed but stops PyCharm removing the import"""
        return Animation(pixel_object, speed, color, name)

else:

    class Animation:
        """
        Stubs out the Animation class.
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


    def __new_animation(pixel_object, speed, color, name=None):
        """Just for consistency"""
        return Animation(pixel_object, speed, color, name)
