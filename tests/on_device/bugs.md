By default 2_validate_button wont work on a board like Tiny 2350 as there
is no board.LED. instead it has board.LED_R, board.LED_G, board.LED_B as
shown here: https://github.com/adafruit/circuitpython/blob/main/ports/raspberrypi/boards/pimoroni_tiny2350/pins.c
Need to abstract away from the board. Onboard button is board.USER_SW

8_validate_network.py running on Graveyard Pico
Running on microcontroller. Pins are available.
No config file was found
Connected to WiFi
IP address:  192.168.1.219
14.502: CRITICAL - MEMORY USAGE: Before creating Objects before gc
14.514: CRITICAL - HEAP: Allocated: 107264 bytes, Free: 16576 bytes
14.538: CRITICAL - MEMORY USAGE: Before creating Objects after gc
14.548: CRITICAL - HEAP: Allocated: 107120 bytes, Free: 16720 bytes
14.646: CRITICAL - MEMORY USAGE: Before running Runner before gc
14.658: CRITICAL - HEAP: Allocated: 114544 bytes, Free: 9296 bytes
14.683: CRITICAL - MEMORY USAGE: Before running Runner after gc
14.695: CRITICAL - HEAP: Allocated: 113568 bytes, Free: 10272 bytes
14.775: INFO - Checking for endpoint expiration.
44.803: INFO - Task completed <closure>
44.865: INFO - Cancelling 3 tasks:
44.869: INFO -   <Task>
44.872: INFO -   <Task>
44.875: INFO -   <Task>
44.879: ERROR - Caught CancelledError exception for task <closure>
44.883: ERROR - Caught CancelledError exception for task <closure>
44.911: ERROR - Caught CancelledError exception for task <closure>
44.916: CRITICAL - MEMORY USAGE: After running Runner before gc
44.927: CRITICAL - HEAP: Allocated: 118752 bytes, Free: 5088 bytes
44.953: CRITICAL - MEMORY USAGE: After running Runner after gc
44.963: CRITICAL - HEAP: Allocated: 117472 bytes, Free: 6368 bytes
PROBLEM IN THONNY'S BACK-END: Exception while handling 'Run' (thonny.plugins.micropython.mp_back.ManagementError:
Command output was not empty).
See Thonny's backend.log for more info.
You may need to press "Stop/Restart" or hard-reset your CircuitPython device and try again.
