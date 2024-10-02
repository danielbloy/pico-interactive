# This is designed to run on a PC and perform the displays of mp4 video files
# on a screen or projector. When the application starts up, it will play the configured
# STARTUP_VIDEO which will prepare the pygame window in full screen mode. A trigger event
# will play the video configured in TRIGGER_VIDEO.
#
# Information on moviepy was from:
# * https://pythonprogramming.altervista.org/play-a-mp4-movie-file-with-pygame-and-moviepy/
#
# TODO: Allow the specification of multiple different videos for trigger events.
# TODO: This should allow for multiple scripted "reels" or purely random displays.
import pygame
from moviepy.editor import *

from interactive.configuration import STARTUP_VIDEO
from interactive.configuration import TRIGGER_DURATION, TRIGGER_VIDEO
from interactive.log import info
from interactive.network import NetworkController
from interactive.polyfills.network import new_server
from interactive.runner import Runner
from interactive.scheduler import new_triggered_task, Triggerable, TriggerTimedEvents

if __name__ == '__main__':

    # TODO: Generate events for playing a 90 second loop or something similar.
    trigger_events = TriggerTimedEvents()
    trigger_events.add_event(00.30, 0)

    trigger_video = VideoFileClip(TRIGGER_VIDEO)


    async def start_display() -> None:
        info("Start display")
        trigger_events.start()


    async def run_display() -> None:
        events = trigger_events.run()

        # TODO: Events are not being generated.
        # TODO: Also fix this in coordinator.

        for event in events:
            # NOTE: Whilst a video is running, the entire runner() framework will be paused.
            if event.event == 0:
                info("Play")
                trigger_video.preview()


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

    # Play a startup video which prepares the screen for full sized video.
    info("Starting up...")
    startup_video = VideoFileClip(STARTUP_VIDEO)
    startup_video.preview()
    del startup_video
    info("Running...")

    runner.run()

    pygame.quit()
