# This file contains common control values.

# These variables control the Runner
RUNNER_DEFAULT_CALLBACK_FREQUENCY = 20  # How many times we expect the callback to be called per second.
RUNNER_DEFAULT_CALLBACK_INTERVAL = 1 / RUNNER_DEFAULT_CALLBACK_FREQUENCY
RUNNER_INTERNAL_LOOP_RATIO = 8

# This is expected the sleep interval for async loops.
ASYNC_LOOP_SLEEP_INTERVAL = 0.001
