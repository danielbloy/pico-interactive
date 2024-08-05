# This module contains utility functions for examining how much RAM the
# system has availale whilst it is running.
#
# Resources:
# * https://learn.adafruit.com/Memory-saving-tips-for-CircuitPython?view=all
# * https://electronics.stackexchange.com/questions/476410/how-to-free-up-memory-in-a-circuitpython-board
# * https://www.adafruitdaily.com/2017/03/31/measure-your-memory-usage-with-mem_info/

# TODO: To determine how much free RAM there is in the system run (this will not count phantom memory as free, run the garbage collector):
import gc
gc.mem_free()



# TODO: Before Interactive runs, we should call the garbage collection and memory manager.
import gc
gc.collect()

# TODO: We should also run the gc.collect() at various points during start up.
# TODO: We need to investigate what is using memory and how expensive:
    * Framework: Interactive
    * Button
    * Buzzer
    * NeoPixels
    * Ultrasonic
    * Audio
    * Network
    
# Memory optimisation:  
# * TODO: Delete large variables using: del <large_variable>
# * TODO: Examine where lists and dictionaries are used as they can grow slowly
# * TODO: Examine all uses of strings