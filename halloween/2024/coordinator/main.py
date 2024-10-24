# This is designed to run on a PC and perform the multi-node coordination.
#
# The Eyes are displayed on the TV on the 1st floor and are kicked off on repeat
# even when the trigger is not activated. The eyes act as an attract to the house.
#
import asyncio

from interactive.configuration import EYES_DURATION, TRIGGER_DURATION
from interactive.log import info
from interactive.network import NetworkController, send_message
from interactive.polyfills.network import new_server
from interactive.runner import Runner
from interactive.scheduler import new_triggered_task, Triggerable, TriggerTimedEvents, new_scheduled_task
from log import critical
from nodes import *

PATH_EVENT = 0
CAULDRON_EVENT = 1
FIRE_EVENT = 2
WITCH_EVENT = 3
GRAVEYARD_EVENT = 4
PROJECTOR_EVENT = 5

event_to_node = [
    PATH,
    CAULDRON,
    FIRE,
    WITCH,
    GRAVEYARD,
    PROJECTOR
]

if __name__ == '__main__':

    runner = Runner()

    runner.cancel_on_exception = False
    runner.restart_on_exception = True
    runner.restart_on_completion = False


    # Trigger the eyes on repeat.
    async def trigger_eyes() -> None:
        asyncio.create_task(trigger_node(EYES))


    runner.add_task(
        new_scheduled_task(
            trigger_eyes,
            frequency=1 / EYES_DURATION,
        ))

    trigger_events = TriggerTimedEvents()
    trigger_events.add_event(00.00, PATH_EVENT)
    trigger_events.add_event(00.00, PROJECTOR_EVENT)
    trigger_events.add_event(01.00, FIRE_EVENT)
    trigger_events.add_event(01.10, CAULDRON_EVENT)
    trigger_events.add_event(01.20, WITCH_EVENT)
    trigger_events.add_event(02.00, GRAVEYARD_EVENT)


    async def trigger_node(node: str) -> None:
        info(f"Triggering {node}")
        send_message("trigger", host=node)


    async def start_display() -> None:
        info("Start display")
        trigger_events.start()


    async def run_display() -> None:
        events = trigger_events.run()

        tasks = []
        for event in events:
            if event.event >= len(event_to_node):
                critical(f"Unknown event: {event.event}")
                continue

            tasks.append(asyncio.create_task(trigger_node(event_to_node[event.event])))


    async def stop_display() -> None:
        info("Stop display")
        trigger_events.stop()


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
