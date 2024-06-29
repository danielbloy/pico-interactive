from interactive.environment import are_pins_available

RED = (255, 0, 0)
"""Red."""
YELLOW = (255, 150, 0)
"""Yellow."""
ORANGE = (255, 40, 0)
"""Orange."""
GREEN = (0, 255, 0)
"""Green."""
TEAL = (0, 255, 120)
"""Teal."""
CYAN = (0, 255, 255)
"""Cyan."""
BLUE = (0, 0, 255)
"""Blue."""
PURPLE = (180, 0, 255)
"""Purple."""
MAGENTA = (255, 0, 20)
"""Magenta."""
WHITE = (255, 255, 255)
"""White."""
BLACK = (0, 0, 0)
"""Black or off."""

GOLD = (255, 222, 30)
"""Gold."""
PINK = (242, 90, 255)
"""Pink."""
AQUA = (50, 255, 255)
"""Aqua."""
JADE = (0, 255, 40)
"""Jade."""
AMBER = (255, 100, 0)
"""Amber."""
OLD_LACE = (253, 245, 230)  # Warm white.
"""Old lace or warm white."""

RGBW_WHITE_RGB = (255, 255, 255, 0)
"""RGBW_WHITE_RGB is for RGBW strips to illuminate only the RGB diodes."""
RGBW_WHITE_W = (0, 0, 0, 255)
"""RGBW_WHITE_W is for RGBW strips to illuminate only White diode."""
RGBW_WHITE_RGBW = (255, 255, 255, 255)
"""RGBW_WHITE_RGBW is for RGBW strips to illuminate the RGB and White diodes."""

RAINBOW = (RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE)

if are_pins_available():
    from adafruit_led_animation.animation import Animation as Animation
    from adafruit_led_animation.sequence import AnimationSequence, AnimateOnce
    from adafruit_led_animation.animation.blink import Blink
    from adafruit_led_animation.animation.chase import Chase
    from adafruit_led_animation.animation.colorcycle import ColorCycle
    from adafruit_led_animation.animation.comet import Comet
    from adafruit_led_animation.animation.pulse import Pulse
    from adafruit_led_animation.animation.rainbow import Rainbow
    from adafruit_led_animation.animation.rainbowchase import RainbowChase
    from adafruit_led_animation.animation.rainbowcomet import RainbowComet
    from adafruit_led_animation.animation.rainbowsparkle import RainbowSparkle
    from adafruit_led_animation.animation.sparkle import Sparkle


    def __hide() -> None:
        """This is not expected to be needed but stops PyCharm removing the import"""
        animation: Animation
        animateOnce: AnimateOnce
        animationSequence: AnimationSequence
        blink: Blink
        chase: Chase
        colorCycle: ColorCycle
        comet: Comet
        pulse: Pulse
        rainbow: Rainbow
        rainbowChase: RainbowChase
        rainbowComet: RainbowComet
        rainbowSparkle: RainbowSparkle
        sparkle: Sparkle


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

        def show(self):
            pass

        def freeze(self):
            pass

        def resume(self):
            pass

        def fill(self, color):
            self.color = color

        def reset(self):
            pass


    class Blink(Animation):

        def _set_color(self, color):
            pass


    class Chase(Animation):

        def __init__(self, pixel_object, speed, color, size=2, spacing=3, reverse=False, name=None):
            self.size = size
            self.spacing = spacing
            self.reverse = reverse
            super().__init__(pixel_object, speed, color, name=name)


    class ColorCycle(Animation):
        def __init__(self, pixel_object, speed, colors=RAINBOW, name=None, start_color=0):
            self.colors = colors
            self.start_color = start_color
            super().__init__(pixel_object, speed, colors[start_color], name=name)


    class Comet(Animation):
        def __init__(self, pixel_object, speed, color, background_color=BLACK, tail_length=0,
                     reverse=False, bounce=False, name=None, ring=False):
            self.background_color = background_color
            self.tail_length = tail_length
            self.reverse = reverse
            self.bounce = bounce
            self.ring = ring
            super().__init__(pixel_object, speed, color, name=name)


    class Pulse(Animation):
        def __init__(self, pixel_object, speed, color, period=5, breath=0,
                     min_intensity=0, max_intensity=1, name=None):
            self.period = period
            self.breath = breath
            self.min_intensity = min_intensity
            self.max_intensity = max_intensity
            super().__init__(pixel_object, speed, color, name=name)


    class Rainbow(Animation):
        def __init__(self, pixel_object, speed, period=5, step=1, name=None, precompute_rainbow=True):
            self._period = period
            self.step = step
            self.colors = None
            self.precompute_rainbow = precompute_rainbow
            super().__init__(pixel_object, speed, BLACK, name=name)

        def generate_rainbow(self):
            pass


    class RainbowChase(Chase):
        def __init__(self, pixel_object, speed, size=2, spacing=3, reverse=False, name=None, step=8):
            self.step = step
            super().__init__(pixel_object, speed, 0, size, spacing, reverse, name)


    class RainbowComet(Comet):
        def __init__(self, pixel_object, speed, tail_length=10, reverse=False, bounce=False,
                     colorwheel_offset=0, step=0, name=None, ring=False):
            self.colorwheel_offset = colorwheel_offset
            self.step = step
            super().__init__(pixel_object, speed, 0, 0, tail_length, reverse, bounce, name, ring)


    class RainbowSparkle(Rainbow):
        def __init__(self, pixel_object, speed, period=5, num_sparkles=None, step=1, name=None,
                     background_brightness=0.2, precompute_rainbow=True):
            self.num_sparkles = num_sparkles
            self.background_brightness = background_brightness
            self.bright_colors = None
            super().__init__(pixel_object=pixel_object, speed=speed, period=period, step=step,
                             name=name, precompute_rainbow=precompute_rainbow)


    class Sparkle(Animation):
        def __init__(self, pixel_object, speed, color, num_sparkles=1, name=None, mask=None):
            self.num_sparkles = num_sparkles
            self.mask = mask
            super().__init__(pixel_object, speed, color, name=name)


    class AnimationSequence:
        def __init__(self, *members, advance_interval=None, auto_clear=True, random_order=False,
                     auto_reset=False, advance_on_cycle_complete=False, name=None):
            self.members = members
            self.advance_interval = advance_interval
            self.auto_clear = auto_clear
            self.random_order = random_order
            self.auto_reset = auto_reset
            self.advance_on_cycle_complete = advance_on_cycle_complete
            self.name = name
            self.current_animation = None
            self.color = None

        def activate(self, index):
            pass

        def next(self):
            pass

        def previous(self):
            pass

        def random(self):
            pass

        def animate(self, show=True):
            pass

        def fill(self, color):
            pass

        def freeze(self):
            pass

        def resume(self):
            pass

        def reset(self):
            pass

        def show(self):
            pass


    class AnimateOnce(AnimationSequence):
        pass
