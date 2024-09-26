# NOTE: Rename this to code.py on the primary node network microcontroller.
#
# This node runs:
# * Network communications
#
# It is connected to two other nodes which each control the skulls for one side of the path:
# * A local path node on the same board:
#   * Controls 6 x skulls, 2 x speakers (plays the dong sounds)
#
# * A remote path node on the other side of the board:
#   * Controls 6 x skulls, 2 x speakers (plays dragon and lion sounds)
#   * Has an ultrasonic sensor to check for a trigger.
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
# * A button press (either node)

from interactive.button import ButtonController
from interactive.configuration import BUTTON_PIN, TRIGGER_DURATION
from interactive.memory import setup_memory_reporting
from interactive.network import NetworkController, receive_blink_message
from interactive.polyfills.button import new_button
from interactive.polyfills.network import new_server
from interactive.runner import Runner
from interactive.scheduler import new_triggered_task, Triggerable

# Because of memory constraints, we do not use the Interactive class here.
# Rather, we setup everything ourselves to minimise what we pull in.
runner = Runner()

runner.cancel_on_exception = False
runner.restart_on_exception = True
runner.restart_on_completion = False


async def start_display() -> None:
    # TODO: Press the button on each path node to trigger it
    receive_blink_message(None)


triggerable = Triggerable()

trigger_loop = new_triggered_task(
    triggerable,
    duration=TRIGGER_DURATION,
    start=start_display)
runner.add_task(trigger_loop)


async def button_press() -> None:
    triggerable.triggered = True


button_controller = ButtonController(new_button(BUTTON_PIN))
button_controller.add_single_press_handler(button_press)
button_controller.register(runner)


def network_trigger() -> None:
    triggerable.triggered = True


server = new_server()
network_controller = NetworkController(server)
network_controller.register(runner)

setup_memory_reporting(runner)
runner.run()
