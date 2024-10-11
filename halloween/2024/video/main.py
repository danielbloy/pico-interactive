# This is designed to run on a PC and perform the display of set of videos. Each time
# the application is triggered, the set of videos to play will be randomly selected
# from the configuration data based on weight. A video set consists of a list of
# videos to play and the timing intervals to play them at.
#
# When the application starts up, it will play the configured STARTUP_VIDEO which will
# prepare the pygame window in full screen mode.
#
# A simplified TRIGGER_VIDEO value dispenses with the more complex TRIGGER_VIDEOS and
# simply overwrites it so that only a single video is played.
#
# Information on moviepy was from:
# * https://pythonprogramming.altervista.org/play-a-mp4-movie-file-with-pygame-and-moviepy/
#
import random

import pygame
from moviepy.editor import *

from config import TRIGGER_VIDEO
from interactive.configuration import STARTUP_VIDEO
from interactive.configuration import TRIGGER_DURATION, TRIGGER_VIDEOS
from interactive.log import info
from interactive.network import NetworkController
from interactive.polyfills.network import new_server
from interactive.runner import Runner
from interactive.scheduler import new_triggered_task, Triggerable, TriggerTimedEvents

if __name__ == '__main__':

    # If a TRIGGER_VIDEO is ever specified then it overwrites TRIGGER_VIDEOS.
    # This is also a useful reference for the expected data structure.
    if TRIGGER_VIDEO:
        TRIGGER_VIDEOS = [
            {
                'weight': 1,
                'videos': [
                    {'time': 0, 'file': TRIGGER_VIDEO}
                ]
            }
        ]

    # For each entry in TRIGGER_VIDEOS, this list will contain its index the number
    # of times weight is specified. This allows us to randomly select a video based
    # on a weighting.
    video_selector = []
    for idx, video_set_details in enumerate(TRIGGER_VIDEOS):
        for i in range(video_set_details['weight']):
            video_selector.append(idx)

    # The index selected to be played.
    video_set = []

    trigger_events = TriggerTimedEvents()


    async def start_display() -> None:
        global video_selector, video_set
        info("Start display")

        # Randomly select a video set to play.
        selected_index = video_selector[random.randint(0, len(video_selector) - 1)]
        video_set = TRIGGER_VIDEOS[selected_index]['videos']

        # Add the video events.
        trigger_events.events.clear()

        for idx, video in enumerate(video_set):
            info(f"{idx} - {video['file']} will play at {video['time']} seconds")
            trigger_events.add_event(video['time'], idx)

        trigger_events.start()


    async def run_display() -> None:
        events = trigger_events.run()

        for event in events:
            # NOTE: Whilst a video is running, the entire runner() framework will be paused.
            info(f"Playing video {event.event} - {video_set[event.event]['file']}")
            trigger_video = VideoFileClip(video_set[event.event]['file'])
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
