#
# With debug=True, there will be lots of errors in the Windows console about a non-blocking operation.
# These are harmless but can be turned off by either disabling debug or changing:
#   sock.setblocking(False)  # Non-blocking socket
#
# To:
#   sock.setblocking(True)  # Non-blocking socket
#
# On line 211 in adafruit_httpserver/server.py
#
# Sample commands to run (see this cheat sheet https://gist.github.com/subfuzion/08c5d85437d5d4f00e58):
#  curl --verbose http://127.0.0.1:5001/
#  curl --verbose http://127.0.0.1:5001/index.html
#  curl --verbose http://127.0.0.1:5001/cpu-information
#  curl --verbose http://127.0.0.1:5001/inspect
#  curl --verbose http://127.0.0.1:5001/register
#  curl --verbose http://127.0.0.1:5001/register -X POST -d "{\"name\":\"daniel\", \"role\":\"programmer\", \"ip\":\"a.b.c.d\"}" -H "Content-Type: application/json"
#  curl --verbose http://127.0.0.1:5001/register -X PUT
#  curl --verbose http://127.0.0.1:5001/unregister
#  curl --verbose http://127.0.0.1:5001/unregister -X POST -d "{\"key1\":\"value1\", \"key2\":\"value2\"}" -H "Content-Type: application/json"
#  curl --verbose http://127.0.0.1:5001/unregister -X PUT
#  curl --verbose http://127.0.0.1:5001/restart
#  curl --verbose http://127.0.0.1:5001/alive
#  curl --verbose http://127.0.0.1:5001/name
#  curl --verbose http://127.0.0.1:5001/role
#  curl --verbose http://127.0.0.1:5001/blink
#
import time

from interactive.button import ButtonController
from interactive.directory import DirectoryService
from interactive.environment import are_pins_available, is_running_on_microcontroller
from interactive.log import set_log_level, info, INFO
from interactive.memory import report_memory_usage_and_free
from interactive.network import NetworkController
from interactive.polyfills.button import new_button
from interactive.polyfills.network import new_server
from interactive.runner import Runner

REPORT_RAM = is_running_on_microcontroller()

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


    runner = Runner()

    button = new_button(BUTTON_PIN)
    button_controller = ButtonController(button)
    button_controller.add_single_press_handler(single_click_handler)
    button_controller.register(runner)

    server = new_server(debug=False)
    network_controller = NetworkController(server)
    network_controller.register(runner)
    directory = DirectoryService()
    network_controller.server.add_routes(directory.get_routes())
    directory.register(runner)

    # Allow the application to only run for a defined number of seconds.
    finish = time.monotonic() + 10


    async def callback() -> None:
        runner.cancel = time.monotonic() > finish


    if REPORT_RAM:
        report_memory_usage_and_free("Before running Runner")

    runner.run(callback)

    if REPORT_RAM:
        report_memory_usage_and_free("After running Runner")
