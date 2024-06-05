from environment import isBlinkaAvailable

if isBlinkaAvailable:
    import board
    GP15 = board.GP15
else:
    GP15 = None

TIMEZONE = "Europe/London"

SLEEP_INTERVAL = 25

# Physical details about the NeoPixels
PIXELS_PIN = GP15
PIXELS_NODES_NUM = 6
PIXELS_PER_NODE = 2

# Control of the pixels. If PIXELS_ON is False, the pixels are always
# off irrespective of PIXELS_ON_TIME or PIXEL_OFF_TIME.
PIXELS_ON = True
PIXELS_BRIGHTNESS = 1.0
PIXELS_SPEED = 1.0
PIXELS_ON_TIME = 1600
PIXEL_OFF_TIME = 2200

# How long each animation runs for.
ANIMATION_DURATION = 60

# Use an empty list to populate all.
ANIMATIONS = [
    "flicker",
    "#blink",
    "#comet",
    "#chase",
    "#cycle",
    "pulse",
    "#sparkle",
    "#rainbow",
    "#rainbow_comet",
    "rainbow_chase",
    "#rainbow_sparkle",
]
