from interactive.environment import is_running_on_desktop
from interactive.polyfills.button import Button
from interactive.runner import Runner

# collections.abc is not available in CircuitPython.
if is_running_on_desktop():
    from collections.abc import Callable, Awaitable


class MicrophoneController:

    def __init__(self, microphone: Microphone):
        if microphone is None:
            raise ValueError("microphone cannot be None")

        if not isinstance(microphone, Microphone):
            raise ValueError("microphone must be of type Microphone")
