import time

from interactive.control import NS_PER_SECOND
from interactive.environment import is_running_on_desktop
from interactive.polyfills.microphone import Microphone
from interactive.runner import Runner

# collections.abc is not available in CircuitPython.
if is_running_on_desktop():
    from collections.abc import Callable, Awaitable


# TODO: Trigger when above threshold (and when come down)
# TODO: Trigger when below threshold (and when go up)
# TODO: Add tests


class MicrophoneController:
    """
    The MicrophoneController class will sample the provided Microphone instance
    at the desired frequency, recording the minimum and maximum values during
    the sample. Each sample will be passed to the provided callback handler
    which can further process the sample. Before the Sample values are passed
    to the callback handler, they are adjusted by the offset value.

    Instances of this class will need to register() with a Runner in order to work.
    """

    def __init__(self, microphone: Microphone, frequency: int = 60, offset: int = 0):
        if microphone is None:
            raise ValueError("microphone cannot be None")

        if not isinstance(microphone, Microphone):
            raise ValueError("microphone must be of type Microphone")

        self.__runner = None
        self.__microphone = microphone
        self.__sample_handler = None
        self.__sampling = False
        self.__next_sample = 0
        self.__offset = offset
        self.__sample_min = microphone.max
        self.__sample_max = microphone.min
        self.frequency = frequency

    @property
    def frequency(self) -> int:
        """
        Returns the frequency of sampling the microphone.
        """
        return self.__frequency

    @frequency.setter
    def frequency(self, value: int) -> None:
        """
        Sets the frequency at which the microphone will be sampled.
        """
        interval = 1 / value
        self.__interval_ns: int = int(interval * NS_PER_SECOND)
        self.__frequency = value

    def add_handler(self, handler: Callable[[int, int], Awaitable[None]] = None):
        """
        Adds a handler for a data sample event. Overwrites any previous handler.

        :param handler: The handler to call to receive the data sample.
        """
        self.__sample_handler = handler

    def start(self):
        """
        Starts the microphone sampling.
        """
        self.__sampling = True
        self.__next_sample = time.monotonic_ns() + self.__interval_ns
        self.__sample_min = self.__microphone.max
        self.__sample_max = self.__microphone.min

    def stop(self):
        """
        Stops the microphone sampling.
        """
        self.__sampling = False

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

        if not self.__sampling:
            return

        if time.monotonic_ns() >= self.__next_sample:

            if self.__sample_handler:
                # If no value was recorded then return minimums.
                if self.__sample_max <= self.__sample_min:
                    self.__sample_min = self.__microphone.min
                    self.__sample_max = self.__microphone.min

                await self.__sample_handler(
                    self.__sample_min - self.__offset,
                    self.__sample_max - self.__offset)

            self.__next_sample += self.__interval_ns
            self.__sample_min = self.__microphone.max
            self.__sample_max = self.__microphone.min

        value = self.__microphone.value

        if value > self.__sample_max:
            self.__sample_max = value
        if value < self.__sample_min:
            self.__sample_min = value
