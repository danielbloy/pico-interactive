# NOTE: Rename this to code.py on the primary node network microcontroller.

# This node runs:
# * Network communications
# * Ultrasonic sensor for trigger
#
# It is connected to two other nodes which each control the skulls for one side of the path:
# * A local path node on the same board:
#   * Controls 6 x skulls, 2 x speakers (plays the dong sounds)
#
# * A remote path node on the other side of the board:
#   * Controls 6 x skulls, 2 x speakers (plays dragon and lion sounds)
#   * Has an ultrasonic sensor to also check for a trigger.
#
# In terms of communications:
# * This node can communicate with the network, indicating a trigger (or force trigger).
# * This node can trigger both the local and remote nodes using a single wire (as a button)
# * The local path node does not communicate back to this node at all.
# * The remote path node can indicate a trigger event (but does nothing about it itself)
#
# The local path node can be triggered by:
# * The ultrasonic sensor
# * A network message
# * A button press

import board

from interactive.configuration import get_node_config
from interactive.framework import Interactive

SKULL_PIXELS_PINS = [board.GP5, board.GP6, board.GP7, board.GP8, board.GP9, board.GP10]


# TODO: Turn on Interactive/Runner restart code.
# TODO: Move the common code for Primary and secondary nodes to a common file.: remember different pins for skulls
# TODO: Hook up button to trigger
# TODO: Hook up network message to trigger
# TODO: Hook up ultrasonic to trigger.

async def cancel() -> None:
    pass


async def start_display() -> None:
    pass


async def run_display() -> None:
    pass


async def stop_display() -> None:
    pass


config = get_node_config(network=True, button=True, buzzer=False, audio=False, ultrasonic=True)
config.trigger_start = start_display()
config.trigger_run = run_display()
config.trigger_stop = stop_display()


async def callback() -> None:
    if interactive.cancel:
        await cancel()


interactive = Interactive(config)

interactive.run(callback)
