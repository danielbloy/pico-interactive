# This is designed to run on a PC and perform the multi-node coordination.
import interactive.control

interactive.control.NETWORK_HOST_DESKTOP = "192.168.1.248"

from interactive.configuration import TRIGGER_DURATION
from interactive.log import info
from interactive.network import NetworkController
from interactive.polyfills.network import new_server
from interactive.runner import Runner
from interactive.scheduler import new_triggered_task, Triggerable

REPORT_RAM = True

if __name__ == '__main__':
    async def start_display() -> None:
        info("Triggered")


    runner = Runner()

    triggerable = Triggerable()

    trigger_loop = new_triggered_task(
        triggerable,
        duration=TRIGGER_DURATION,
        start=start_display)
    runner.add_task(trigger_loop)


    def network_trigger() -> None:
        triggerable.triggered = True


    server = new_server()
    network_controller = NetworkController(server, network_trigger)
    network_controller.register(runner)

    runner.run()
