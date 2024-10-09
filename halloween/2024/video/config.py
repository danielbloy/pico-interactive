TRIGGER_DURATION = 40

STARTUP_VIDEO = "startup.mp4"
# When set to a value, TRIGGER_VIDEO overrides TRIGGER_VIDEOS and
# allows for a simple method to simply display a single video. To
# use the more powerful TRIGGER_VIDEOS, set TRIGGER_VIDEO to None.
TRIGGER_VIDEO = "skeleton.mp4"
# TRIGGER_VIDEO = None

TRIGGER_VIDEOS = [
    {
        'weight': 1,
        'videos': [
            {'time': 10.2, 'file': 'scare-death.mp4'}
        ]
    },
    {
        'weight': 1,
        'videos': [
            {'time': 0.5, 'file': 'scare-siren.mp4'},
            {'time': 25, 'file': 'scare-poltergeist.mp4'}
        ]
    },
    {
        'weight': 1,
        'videos': [
            {'time': 1.4, 'file': 'scare-spinster.mp4'},
            {'time': 20, 'file': 'scare-wraith.mp4'}
        ]
    },
    {
        'weight': 3,
        'videos': [
            {'time': 0.5, 'file': 'marley.mp4'},
            {'time': 24, 'file': 'skeleton.mp4'}
        ]
    }
]

from interactive.log import INFO

LOG_LEVEL = INFO
