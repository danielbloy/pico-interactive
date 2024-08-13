#
# With debug=True, there will be lots of errors in Windows about a non-blocking operation.
# These are harmless but can be turned off by either disabling debug or changing:
#   sock.setblocking(False)  # Non-blocking socket
#
# To:
#   sock.setblocking(True)  # Non-blocking socket
#
# On line 211 in adafruit_httpserver/server.py
#
import time

from interactive.button import ButtonController
from interactive.environment import are_pins_available
from interactive.log import set_log_level, info, INFO
from interactive.memory import report_memory_usage_and_free
from interactive.network import NetworkController
from interactive.polyfills.button import new_button
from interactive.polyfills.network import new_server
from interactive.runner import Runner

REPORT_RAM = are_pins_available()

BUTTON_PIN = None

if are_pins_available():
    # noinspection PyPackageRequirements
    import board

    BUTTON_PIN = board.GP27

if __name__ == '__main__':

    set_log_level(INFO)

    if REPORT_RAM:
        report_memory_usage_and_free("Before creating Objects")


    async def single_click_handler() -> None:
        info('Single click!')
        # TODO: Send message


    runner = Runner()

    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_click_handler(single_click_handler)
    button_controller.register(runner)

    server = new_server(debug=False)
    network_controller = NetworkController(server)
    network_controller.register(runner)

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + 30


    async def callback() -> None:
        runner.cancel = time.monotonic() > finish


    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    runner.run(callback)

    if REPORT_RAM:
        report_memory_usage_and_free("After running Runner")
