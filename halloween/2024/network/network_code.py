# This is common code that runs the network device in each node. It has
# a capability to be trigger two nodes, a remote and local. The host node
# can configure what that means. The config.py file must setup the following
# properties:
#   * BUTTON_PIN
#   * TRIGGER_DURATION
#   * LOCAL_TRIGGER_PIN
#   * REMOTE_TRIGGER_PIN
import asyncio

from digitalio import Direction, DigitalInOut

from interactive.button import ButtonController
from interactive.configuration import BUTTON_PIN, TRIGGER_DURATION
from interactive.configuration import LOCAL_TRIGGER_PIN, REMOTE_TRIGGER_PIN
from interactive.memory import setup_memory_reporting
from interactive.network import NetworkController
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

local = DigitalInOut(LOCAL_TRIGGER_PIN)
local.direction = Direction.OUTPUT
local.value = 1

remote = DigitalInOut(REMOTE_TRIGGER_PIN)
remote.direction = Direction.OUTPUT
remote.value = 1


async def start_display() -> None:
    local.value = 0
    remote.value = 0
    await asyncio.sleep(0.05)
    local.value = 1
    remote.value = 1


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
network_controller = NetworkController(server, network_trigger)
network_controller.register(runner)

setup_memory_reporting(runner)
runner.run()
