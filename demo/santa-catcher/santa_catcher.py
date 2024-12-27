# This is designed to run on a Plasma 2350 (or 2350 W).
#

import board

from interactive.button import ButtonController
from interactive.led import Led
from interactive.log import set_log_level, INFO
from interactive.microphone import MicrophoneController
from interactive.polyfills.animation import BLACK
from interactive.polyfills.button import new_button
from interactive.polyfills.led import new_led_pin
from interactive.polyfills.microphone import Microphone
from interactive.polyfills.pixel import new_pixels
from interactive.runner import Runner
from interactive.scheduler import new_scheduled_task

BUTTON_PIN = board.BUTTON
LED_BLUE = board.LED_B
LED_GREEN = board.LED_G
LED_RED = board.LED_R
PIXELS_PIN = board.GP15

MICROPHONE_PIN = board.A0

set_log_level(INFO)

runner = Runner()


async def single_click_handler() -> None:
    if not runner.cancel:
        global detection_screen
        detection_screen += 1
        detection_screen %= DETECTION_SCREENS

        reset_animations()

        display.fill(OFF)


stop = False


async def long_press_handler() -> None:
    global stop
    stop = True


button = new_button(BUTTON_PIN)
button_controller = ButtonController(button)
button_controller.add_single_press_handler(single_click_handler)
button_controller.add_long_press_handler(long_press_handler)
button_controller.register(runner)

# Framework for onboard LEDs
blue = Led(new_led_pin(LED_BLUE))
green = Led(new_led_pin(LED_GREEN))
red = Led(new_led_pin(LED_RED))

# Framework for pixels and microphone.
# See this example: https://learn.adafruit.com/easy-neopixel-graphics-with-the-circuitpython-pixel-framebuf-library
from adafruit_pixel_framebuf import PixelFramebuffer, VERTICAL

WIDTH = 20
HEIGHT = 20
FRAME_RATE = 5

pixels = new_pixels(PIXELS_PIN, WIDTH * HEIGHT, brightness=0.5)

display = PixelFramebuffer(
    pixels,
    WIDTH,
    HEIGHT,
    orientation=VERTICAL,
    alternating=False,
    rotation=0)

display.fill(0x000000)
display.display()

microphone = Microphone(MICROPHONE_PIN)
microphone_controller = MicrophoneController(microphone, frequency=FRAME_RATE)
microphone_controller.register(runner)

SENSITIVITY_FACTOR = 10

# Colours are in GRB form
GREEN = 0xFF_00_00
YELLOW = 0xFF_FF_00
ORANGE = 0x45_FF_00
RED = 0x00_FF_00
SANTA_RED = 0x00_C9_00  # RGB: C9 00 00 -> GRB: 00 C9 00
SANTA_BLUE = 0x7C_10_AB  # RGB: 10 7C AB -> GRB: 7C 10 AB
SKIN = 0x_96_D7_78  # RGB: D7 96 78 -> 96 D7 78
BLUE = 0x00_00_FF
WHITE = 0xFF_FF_FF
LIGHT_BLUE = 0xD2_7C_C8  # RGB: 7C D2 C8 -> GRB: D2 7C C8
OFF = 0x000000


def reset_animations():
    global santa_pos_x, santa_pos_y, santa_direction
    santa_pos_x = -5
    santa_pos_y = 0
    santa_direction = 1


santa_pos_x = -5
santa_pos_y = 0
santa_direction = 1

santa = """
..........ww........
.........rww........
........rrr.........
.......rrrrr........
......rrrrrrr.......
......rwwwwwr.......
......wsbsbsw.......
...g..wsssssw..g....
.ggg..wwwwwww..ggg..
.gggrrwwwwwwwrrggg..
..grrrrwwwwwrrrg....
...rrrrrwwwrrrrr....
......rrrwrrr.......
......rrrrrrr.......
......rrrrrrr.......
.....wwwwwwwww......
.....wwwwwwwww......
......bbb.bbb.......
.....bbbb.bbbb......
.....bbbb.bbbb......
"""
santa_palette = {
    "r": SANTA_RED,
    "g": GREEN,
    "w": WHITE,
    "b": SANTA_BLUE,
    "s": SKIN,
}

message = """
qqqqqqqqqqqqqqqqqqqq
rrrqrrrqrrrqrrrqrrrq
rqqqrqrqrqrqqrqqrqrq
rqqqrqrqrqrqqrqqrqrq
rrrqrrrqrqrqqrqqrrrq
qqrqrqrqrqrqqrqqrqrq
qqrqrqrqrqrqqrqqrqrq
rqrqrqrqrqrqqrqqrqrq
qqqqqqqqqqqqqqqqqqqq
qqqqqqqqqqqqqqqqqqqq
"""
message_palette = {
    "r": SANTA_RED,
    "q": OFF,
}

detection_mode = True
alert_mode = not detection_mode

detection_screen = 0
DETECTION_SCREENS = 2

alert_screen = 0
ALERT_SCREENS = 2
alert_duration = 0  # How many seconds left in alert mode.


async def alert_or_detection_mode() -> None:
    global alert_duration
    alert_duration -= 1
    if alert_duration < 0:
        alert_duration = 0

    global detection_mode
    if alert_mode and alert_duration <= 0:
        display.fill(OFF)

    detection_mode = alert_duration <= 0


scheduled_task = new_scheduled_task(alert_or_detection_mode, frequency=1)
runner.add_loop_task(scheduled_task)


def draw_picture(origin_x, origin_y, picture, palette):
    for y, line in enumerate(picture.splitlines()):
        for x, colour in enumerate(line):
            if colour != ".":
                display.pixel(origin_x + x, origin_y + y, palette[colour])


def display_sound_as_bar_chart(minimum, maximum, bar_height: int):
    # Just report amplitude along the bottom of the screen to a maximum height.
    display.scroll(-1, 0)

    amplitude = maximum - minimum
    divisor = (microphone.max / bar_height) / SENSITIVITY_FACTOR
    height = min(int(amplitude / divisor), bar_height)

    # Start with default colours for the bar and then blank out those that we don't need.
    colours = [GREEN, GREEN, GREEN, YELLOW, YELLOW, YELLOW, ORANGE, ORANGE, RED, RED]
    if bar_height > 10:
        colours = [GREEN, GREEN, GREEN, GREEN, GREEN, YELLOW, YELLOW, YELLOW, YELLOW, YELLOW, ORANGE, ORANGE, ORANGE,
                   ORANGE, ORANGE, RED, RED, RED, RED, RED]

    for idx in range(bar_height - height):
        colours[bar_height - idx - 1] = OFF

    for idx, colour in enumerate(colours):
        display.pixel(WIDTH - 1, HEIGHT - 1 - idx, colour)


# This indicates the current frame within each second. Each second we will draw FRAME_RATE
# This loops around to zero
frame = -1


async def draw_screen(minimum, maximum: int) -> None:
    global frame
    frame += 1
    frame %= FRAME_RATE

    global detection_mode, alert_mode

    if detection_mode:
        # We move to alert mode if we get a 80% signal. This applies to the next frame.
        amplitude = maximum - minimum
        divisor = (microphone.max / 100) / SENSITIVITY_FACTOR
        height = min(int(amplitude / divisor), 100)
        alert_mode = height >= 80

        # If we are switching into alert mode, then set the timer for 15 seconds.
        if alert_mode:
            global alert_duration, alert_screen
            alert_duration += 15
            alert_screen += 1
            alert_screen %= ALERT_SCREENS

        detection_mode = not alert_mode

        global detection_screen
        if detection_screen == 0:
            display_sound_as_bar_chart(minimum, maximum, int(HEIGHT / 2))
            draw_picture(0, 0, message, message_palette)

        elif detection_screen == 1:
            display_sound_as_bar_chart(minimum, maximum, HEIGHT)

    if alert_mode:
        global alert_screen
        if alert_screen == 0:
            # change only on frame 0
            if frame == 0:
                display.fill(OFF)
                import random
                display.text("Ho", random.randint(0, 9), 0, SANTA_RED)
                display.text("Ho", random.randint(0, 9), 10, SANTA_RED)

        elif alert_screen == 1:
            global santa_pos_x, santa_pos_y, santa_direction
            display.fill(OFF)
            draw_picture(santa_pos_x, santa_pos_y, santa, santa_palette)
            santa_pos_x += santa_direction
            if santa_pos_x >= 10 or santa_pos_x <= -5:
                santa_direction *= -1

    display.display()


microphone_controller.add_handler(draw_screen)
microphone_controller.start()


async def callback() -> None:
    global stop
    runner.cancel = stop
    if runner.cancel:
        microphone_controller.stop()

        red.off()
        green.off()
        blue.off()

        red.show()
        green.show()
        blue.show()

        pixels.fill(BLACK)
        pixels.write()


runner.run(callback)
