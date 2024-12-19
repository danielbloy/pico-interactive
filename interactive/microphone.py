from interactive.environment import is_running_on_desktop
from interactive.polyfills.microphone import Microphone
from interactive.runner import Runner

# collections.abc is not available in CircuitPython.
if is_running_on_desktop():
    pass


class MicrophoneController:
    """
    TODO: Have a callback when each quantised value is returned
    # TODO: Should this create a subtask when playing or use the update method.

    Instances of this class will need to register() with a Runner in order to work.
    """

    def __init__(self, microphone: Microphone, sample_rate=44100):
        if microphone is None:
            raise ValueError("microphone cannot be None")

        if not isinstance(microphone, Microphone):
            raise ValueError("microphone must be of type Microphone")

        self.__runner = None
        self.__microphone = microphone
        self.recording = False
        self.sample_rate = sample_rate

    # TODO: Add recording handler

    def register(self, runner: Runner) -> None:
        """
        Registers this MicrophoneController instance as a task with the provided Runner.

        :param runner: the runner to register with.
        """
        self.__runner = runner
        runner.add_loop_task(self.__loop)

    async def __loop(self):
        """
        The internal loop simply invokes the correct handler based on the microphone state.
        """
        if self.__runner.cancel:
            return

        if not self.recording:
            return

        # TODO: need to convert the value which is clamped from min to max into an
        #       ordinal value from zero to 100% (also include the raw value).
