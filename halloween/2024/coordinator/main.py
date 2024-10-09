# This is designed to run on a PC and perform the multi-node coordination.

from interactive.configuration import TRIGGER_DURATION
from interactive.log import info
from interactive.network import NetworkController
from interactive.polyfills.network import new_server
from interactive.runner import Runner
from interactive.scheduler import new_triggered_task, Triggerable, TriggerTimedEvents

if __name__ == '__main__':

    trigger_events = TriggerTimedEvents()
    trigger_events.add_event(00.30, 0)
    trigger_events.add_event(02.70, 1)


    async def start_display() -> None:
        info("Start display")
        trigger_events.start()


    async def run_display() -> None:
        events = trigger_events.run()

        for event in events:
            pass  # TODO: Implement, performing all separate network requests asynchronously.


    async def stop_display() -> None:
        info("Stop display")
        trigger_events.stop()


    runner = Runner()

    runner.cancel_on_exception = False
    runner.restart_on_exception = True
    runner.restart_on_completion = False

    triggerable = Triggerable()

    trigger_loop = new_triggered_task(
        triggerable,
        duration=TRIGGER_DURATION,
        start=start_display,
        run=run_display,
        stop=stop_display)
    runner.add_task(trigger_loop)


    def network_trigger() -> None:
        triggerable.triggered = True


    server = new_server()
    network_controller = NetworkController(server, network_trigger)
    network_controller.register(runner)

    runner.run()
