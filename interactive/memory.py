# This module contains utility functions for examining how much RAM the
# system has available whilst it is running.
#
# Resources:
# * https://learn.adafruit.com/Memory-saving-tips-for-CircuitPython?view=all
# * https://electronics.stackexchange.com/questions/476410/how-to-free-up-memory-in-a-circuitpython-board
# * https://www.adafruitdaily.com/2017/03/31/measure-your-memory-usage-with-mem_info/
#

import gc


def report_memory_usage(msg: str):
    print(f"MEMORY USAGE: {msg}")
    print(f"HEAP: Allocated: {gc.mem_alloc()} bytes, Free: {gc.mem_free()} bytes")


def report_memory_usage_and_free(msg: str):
    report_memory_usage(f"{msg} before gc")
    gc.collect()
    report_memory_usage(f"{msg} after gc")

# Memory usage results after running each of the on_device validate scripts:
#
# 1 - Framework:
#
#    10 second run:
#    Running on a microcontroller. Pins are available.
#    MEMORY USAGE: Before creating Objects before gc
#    HEAP: Allocated: 23984 bytes, Free: 101392 bytes
#    MEMORY USAGE: Before creating Objects after gc
#    HEAP: Allocated: 23920 bytes, Free: 101456 bytes
#    MEMORY USAGE: Before running Runner before gc
#    HEAP: Allocated: 24448 bytes, Free: 100928 bytes
#    MEMORY USAGE: Before running Runner after gc
#    HEAP: Allocated: 24096 bytes, Free: 101280 bytes
#    MEMORY USAGE: After running Runner before gc
#    HEAP: Allocated: 38128 bytes, Free: 87248 bytes
#    MEMORY USAGE: After running Runner after gc
#    HEAP: Allocated: 27184 bytes, Free: 98192 bytes
#
# 2 - Button:
#
#    10 second run:
#    Running on a microcontroller. Pins are available.
#    MEMORY USAGE: Before creating Objects before gc
#    HEAP: Allocated: 30336 bytes, Free: 95040 bytes
#    MEMORY USAGE: Before creating Objects after gc
#    HEAP: Allocated: 30288 bytes, Free: 95088 bytes
#    MEMORY USAGE: Before running Runner before gc
#    HEAP: Allocated: 31264 bytes, Free: 94112 bytes
#    MEMORY USAGE: Before running Runner after gc
#    HEAP: Allocated: 30864 bytes, Free: 94512 bytes
#    MEMORY USAGE: After running Runner before gc
#    HEAP: Allocated: 50448 bytes, Free: 74928 bytes
#    MEMORY USAGE: After running Runner after gc
#    HEAP: Allocated: 33600 bytes, Free: 91776 bytes
#
# 3 - Buzzer:
#
#    10 second run:
#    Running on a microcontroller. Pins are available.
#    MEMORY USAGE: Before creating Objects before gc
#    HEAP: Allocated: 36880 bytes, Free: 88496 bytes
#    MEMORY USAGE: Before creating Objects after gc
#    HEAP: Allocated: 36816 bytes, Free: 88560 bytes
#    MEMORY USAGE: Before running Runner before gc
#    HEAP: Allocated: 40528 bytes, Free: 84848 bytes
#    MEMORY USAGE: Before running Runner after gc
#    HEAP: Allocated: 38384 bytes, Free: 86992 bytes
#    MEMORY USAGE: After running Runner before gc
#    HEAP: Allocated: 54576 bytes, Free: 70800 bytes
#    MEMORY USAGE: After running Runner after gc
#    HEAP: Allocated: 41968 bytes, Free: 83408 bytes
#
# 4 - Animations:
#
#    10 second run:
#    Running on a microcontroller. Pins are available.
#    MEMORY USAGE: Before creating Objects before gc
#    HEAP: Allocated: 58032 bytes, Free: 67344 bytes
#    MEMORY USAGE: Before creating Objects after gc
#    HEAP: Allocated: 58000 bytes, Free: 67376 bytes
#    MEMORY USAGE: Before running Runner before gc
#    HEAP: Allocated: 92368 bytes, Free: 31760 bytes
#    MEMORY USAGE: Before running Runner after gc
#    HEAP: Allocated: 85776 bytes, Free: 38352 bytes
#    MEMORY USAGE: After running Runner before gc
#    HEAP: Allocated: 92192 bytes, Free: 31936 bytes
#    MEMORY USAGE: After running Runner after gc
#    HEAP: Allocated: 89728 bytes, Free: 34400 bytes
#
# 5 - Interactive: (the only test to use Interactive)
#
#    10 second run:
#    Running on a microcontroller. Pins are available.
#    MEMORY USAGE: Before creating Objects before gc
#    HEAP: Allocated: 41072 bytes, Free: 84304 bytes
#    MEMORY USAGE: Before creating Objects after gc
#    HEAP: Allocated: 41056 bytes, Free: 84320 bytes
#    MEMORY USAGE: Before running Runner before gc
#    HEAP: Allocated: 42448 bytes, Free: 82928 bytes
#    MEMORY USAGE: Before running Runner after gc
#    HEAP: Allocated: 42288 bytes, Free: 83088 bytes
#    MEMORY USAGE: After running Runner before gc
#    HEAP: Allocated: 60080 bytes, Free: 65296 bytes
#    MEMORY USAGE: After running Runner after gc
#    HEAP: Allocated: 45856 bytes, Free: 79520 bytes
#
# 6 - Ultrasonic:
#
#    10 second run:
#    Running on a microcontroller. Pins are available.
#    MEMORY USAGE: Before creating Objects before gc
#    HEAP: Allocated: 34528 bytes, Free: 90848 bytes
#    MEMORY USAGE: Before creating Objects after gc
#    HEAP: Allocated: 34512 bytes, Free: 90864 bytes
#    MEMORY USAGE: Before running Runner before gc
#    HEAP: Allocated: 36240 bytes, Free: 89136 bytes
#    MEMORY USAGE: Before running Runner after gc
#    HEAP: Allocated: 35824 bytes, Free: 89552 bytes
#    MEMORY USAGE: After running Runner before gc
#    HEAP: Allocated: 39712 bytes, Free: 85664 bytes
#    MEMORY USAGE: After running Runner after gc
#    HEAP: Allocated: 38928 bytes, Free: 86448 bytes
#
#    60 second run:
#    Running on a microcontroller. Pins are available.
#    MEMORY USAGE: Before creating Objects before gc
#    HEAP: Allocated: 34528 bytes, Free: 90848 bytes
#    MEMORY USAGE: Before creating Objects after gc
#    HEAP: Allocated: 34512 bytes, Free: 90864 bytes
#    MEMORY USAGE: Before running Runner before gc
#    HEAP: Allocated: 36240 bytes, Free: 89136 bytes
#    MEMORY USAGE: Before running Runner after gc
#    HEAP: Allocated: 35824 bytes, Free: 89552 bytes
#    MEMORY USAGE: After running Runner before gc
#    HEAP: Allocated: 62544 bytes, Free: 62832 bytes
#    MEMORY USAGE: After running Runner after gc
#    HEAP: Allocated: 38928 bytes, Free: 86448 bytes
#
# 7 - Audio:
#
#    10 second run:
#    Running on a microcontroller. Pins are available.
#    MEMORY USAGE: Before creating Objects before gc
#    HEAP: Allocated: 32592 bytes, Free: 92784 bytes
#    MEMORY USAGE: Before creating Objects after gc
#    HEAP: Allocated: 32528 bytes, Free: 92848 bytes
#    MEMORY USAGE: Before running Runner before gc
#    HEAP: Allocated: 68768 bytes, Free: 55360 bytes
#    MEMORY USAGE: Before running Runner after gc
#    HEAP: Allocated: 68768 bytes, Free: 55360 bytes
#    MEMORY USAGE: After running Runner before gc
#    HEAP: Allocated: 79648 bytes, Free: 44480 bytes
#    MEMORY USAGE: After running Runner after gc
#    HEAP: Allocated: 72048 bytes, Free: 52080 bytes
#

#
# Memory optimisation:  
# * TODO: Delete large variables using: del <large_variable>
# * TODO: Examine where lists and dictionaries are used as they can grow slowly
# * TODO: Examine all uses of strings
