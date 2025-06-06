This file contains details of memory usage analysis using the `interactive` framework.
Memory is tight on the Pico 2040 when using this framework. The Pico 2 2350 has much more
RAM available, so use that where possible.

## Resources

* https://learn.adafruit.com/Memory-saving-tips-for-CircuitPython?view=all
* https://electronics.stackexchange.com/questions/476410/how-to-free-up-memory-in-a-circuitpython-board
* https://www.adafruitdaily.com/2017/03/31/measure-your-memory-usage-with-mem_info/

Memory optimisation tips:

* Delete large variables using: del <large_variable>
* Examine where lists and dictionaries are used as they can grow slowly.
* Be careful with string usage as each string created requires its own space.

Very, very rough results (from before running Runner, before gc on Pico W):

1. Runner ....... : 24 Kb
2. Button ....... : 31 Kb, uses about 7kb
3. Buzzer ....... : 40 Kb, uses about 9kb
4. Animations ... : 92 Kb, uses about 31 Kb
5. Interactive .. : 42 Kb, uses about 2 Kb
6. Ultrasonic ... : 36 Kb, uses about 5 Kb
7. Audio ........ : 86 Kb, uses about 35 Kb
8. Network ...... : 105 Kb, uses about 74 Kb

Results also indicate that running the Pico W variant of CircuitPython uses an
extra 40Kb of RAM compared to the plain pico CircuitPython build that does not
include the network stack.

Combinations:

* Runner + Button + Audio + Pixels ........ :
* Runner + Button + Ultrasonic + Network .. :

Memory usage results after running each of the on_device validate scripts:

### 1 - Runner

10 second run (pico W):

```
Running on a microcontroller. Pins are available.
MEMORY USAGE: Before creating Objects before gc
HEAP: Allocated: 23984 bytes, Free: 101392 bytes
MEMORY USAGE: Before creating Objects after gc
HEAP: Allocated: 23920 bytes, Free: 101456 bytes
MEMORY USAGE: Before running Runner before gc
HEAP: Allocated: 24448 bytes, Free: 100928 bytes
MEMORY USAGE: Before running Runner after gc
HEAP: Allocated: 24096 bytes, Free: 101280 bytes
MEMORY USAGE: After running Runner before gc
HEAP: Allocated: 38128 bytes, Free: 87248 bytes
MEMORY USAGE: After running Runner after gc
HEAP: Allocated: 27184 bytes, Free: 98192 bytes
```

10 second run (pico):

```
Running on a microcontroller. Pins are available.
MEMORY USAGE: Before creating Objects before gc
HEAP: Allocated: 24512 bytes, Free: 141760 bytes
MEMORY USAGE: Before creating Objects after gc
HEAP: Allocated: 24496 bytes, Free: 141776 bytes
MEMORY USAGE: Before running Runner before gc
HEAP: Allocated: 25968 bytes, Free: 140304 bytes
MEMORY USAGE: Before running Runner after gc
HEAP: Allocated: 24736 bytes, Free: 141536 bytes
MEMORY USAGE: After running Runner before gc
HEAP: Allocated: 45888 bytes, Free: 120384 bytes
MEMORY USAGE: After running Runner after gc
HEAP: Allocated: 28080 bytes, Free: 138192 bytes
```

### 2 - Runner + Button:

10 second run (pico W):

```
Running on a microcontroller. Pins are available.
MEMORY USAGE: Before creating Objects before gc
HEAP: Allocated: 30336 bytes, Free: 95040 bytes
MEMORY USAGE: Before creating Objects after gc
HEAP: Allocated: 30288 bytes, Free: 95088 bytes
MEMORY USAGE: Before running Runner before gc
HEAP: Allocated: 31264 bytes, Free: 94112 bytes
MEMORY USAGE: Before running Runner after gc
HEAP: Allocated: 30864 bytes, Free: 94512 bytes
MEMORY USAGE: After running Runner before gc
HEAP: Allocated: 50448 bytes, Free: 74928 bytes
MEMORY USAGE: After running Runner after gc
HEAP: Allocated: 33600 bytes, Free: 91776 bytes
```

10 second run (pico):

```
Running on a microcontroller. Pins are available.
MEMORY USAGE: Before creating Objects before gc
HEAP: Allocated: 30944 bytes, Free: 135328 bytes
MEMORY USAGE: Before creating Objects after gc
HEAP: Allocated: 30896 bytes, Free: 135376 bytes
MEMORY USAGE: Before running Runner before gc
HEAP: Allocated: 32736 bytes, Free: 133536 bytes
MEMORY USAGE: Before running Runner after gc
HEAP: Allocated: 31472 bytes, Free: 134800 bytes
MEMORY USAGE: After running Runner before gc
HEAP: Allocated: 46816 bytes, Free: 119456 bytes
MEMORY USAGE: After running Runner after gc
HEAP: Allocated: 34208 bytes, Free: 132064 bytes
```

### 3 - Runner + Button + Buzzer:

10 second run (pico W):

```
Running on a microcontroller. Pins are available.
MEMORY USAGE: Before creating Objects before gc
HEAP: Allocated: 36880 bytes, Free: 88496 bytes
MEMORY USAGE: Before creating Objects after gc
HEAP: Allocated: 36816 bytes, Free: 88560 bytes
MEMORY USAGE: Before running Runner before gc
HEAP: Allocated: 40528 bytes, Free: 84848 bytes
MEMORY USAGE: Before running Runner after gc
HEAP: Allocated: 38384 bytes, Free: 86992 bytes
MEMORY USAGE: After running Runner before gc
HEAP: Allocated: 54576 bytes, Free: 70800 bytes
MEMORY USAGE: After running Runner after gc
HEAP: Allocated: 41968 bytes, Free: 83408 bytes
```

10 second run (pico):

```
Running on a microcontroller. Pins are available.
MEMORY USAGE: Before creating Objects before gc
HEAP: Allocated: 37488 bytes, Free: 128784 bytes
MEMORY USAGE: Before creating Objects after gc
HEAP: Allocated: 37424 bytes, Free: 128848 bytes
MEMORY USAGE: Before running Runner before gc
HEAP: Allocated: 42000 bytes, Free: 124272 bytes
MEMORY USAGE: Before running Runner after gc
HEAP: Allocated: 38960 bytes, Free: 127312 bytes
MEMORY USAGE: After running Runner before gc
HEAP: Allocated: 43760 bytes, Free: 122512 bytes
MEMORY USAGE: After running Runner after gc
HEAP: Allocated: 42544 bytes, Free: 123728 bytes
```

### 4 - Runner + Button + Animations (on LEDs and NeoPixels):

10 second run (pico W):

```
Running on a microcontroller. Pins are available.
MEMORY USAGE: Before creating Objects before gc
HEAP: Allocated: 58032 bytes, Free: 67344 bytes
MEMORY USAGE: Before creating Objects after gc
HEAP: Allocated: 58000 bytes, Free: 67376 bytes
MEMORY USAGE: Before running Runner before gc
HEAP: Allocated: 92368 bytes, Free: 31760 bytes
MEMORY USAGE: Before running Runner after gc
HEAP: Allocated: 85776 bytes, Free: 38352 bytes
MEMORY USAGE: After running Runner before gc
HEAP: Allocated: 92192 bytes, Free: 31936 bytes
MEMORY USAGE: After running Runner after gc
HEAP: Allocated: 89728 bytes, Free: 34400 bytes
```

10 second run (pico):

```
Running on a microcontroller. Pins are available.
MEMORY USAGE: Before creating Objects before gc
HEAP: Allocated: 58848 bytes, Free: 103968 bytes
MEMORY USAGE: Before creating Objects after gc
HEAP: Allocated: 58816 bytes, Free: 104000 bytes
MEMORY USAGE: Before running Runner before gc
HEAP: Allocated: 93088 bytes, Free: 69728 bytes
MEMORY USAGE: Before running Runner after gc
HEAP: Allocated: 86496 bytes, Free: 76320 bytes
MEMORY USAGE: After running Runner before gc
HEAP: Allocated: 114784 bytes, Free: 48032 bytes
MEMORY USAGE: After running Runner after gc
HEAP: Allocated: 90464 bytes, Free: 72352 bytes
```

### 5 - Interactive (Runner + Button + Buzzer):

10 second run (pico W):

```
Running on a microcontroller. Pins are available.
MEMORY USAGE: Before creating Objects before gc
HEAP: Allocated: 41072 bytes, Free: 84304 bytes
MEMORY USAGE: Before creating Objects after gc
HEAP: Allocated: 41056 bytes, Free: 84320 bytes
MEMORY USAGE: Before running Runner before gc
HEAP: Allocated: 42448 bytes, Free: 82928 bytes
MEMORY USAGE: Before running Runner after gc
HEAP: Allocated: 42288 bytes, Free: 83088 bytes
MEMORY USAGE: After running Runner before gc
HEAP: Allocated: 60080 bytes, Free: 65296 bytes
MEMORY USAGE: After running Runner after gc
HEAP: Allocated: 45856 bytes, Free: 79520 bytes
```

10 second run (pico):

```
Running on a microcontroller. Pins are available.
No config file was found
MEMORY USAGE: Before creating Objects before gc
HEAP: Allocated: 31888 bytes, Free: 134384 bytes
MEMORY USAGE: Before creating Objects after gc
HEAP: Allocated: 31824 bytes, Free: 134448 bytes
MEMORY USAGE: Before running Runner before gc
HEAP: Allocated: 39408 bytes, Free: 126864 bytes
MEMORY USAGE: Before running Runner after gc
HEAP: Allocated: 39408 bytes, Free: 126864 bytes
MEMORY USAGE: After running Runner before gc
HEAP: Allocated: 46720 bytes, Free: 119552 bytes
MEMORY USAGE: After running Runner after gc
HEAP: Allocated: 43024 bytes, Free: 123248 bytes
```

### 6 - Runner + Button + Ultrasonic:

10 second run (pico W):

```
Running on a microcontroller. Pins are available.
MEMORY USAGE: Before creating Objects before gc
HEAP: Allocated: 34528 bytes, Free: 90848 bytes
MEMORY USAGE: Before creating Objects after gc
HEAP: Allocated: 34512 bytes, Free: 90864 bytes
MEMORY USAGE: Before running Runner before gc
HEAP: Allocated: 36240 bytes, Free: 89136 bytes
MEMORY USAGE: Before running Runner after gc
HEAP: Allocated: 35824 bytes, Free: 89552 bytes
MEMORY USAGE: After running Runner before gc
HEAP: Allocated: 39712 bytes, Free: 85664 bytes
MEMORY USAGE: After running Runner after gc
HEAP: Allocated: 38928 bytes, Free: 86448 bytes
```

10 second run (pico):

```
Running on a microcontroller. Pins are available.
MEMORY USAGE: Before creating Objects before gc
HEAP: Allocated: 35168 bytes, Free: 131104 bytes
MEMORY USAGE: Before creating Objects after gc
HEAP: Allocated: 35152 bytes, Free: 131120 bytes
MEMORY USAGE: Before running Runner before gc
HEAP: Allocated: 37744 bytes, Free: 128528 bytes
MEMORY USAGE: Before running Runner after gc
HEAP: Allocated: 36464 bytes, Free: 129808 bytes
MEMORY USAGE: After running Runner before gc
HEAP: Allocated: 52272 bytes, Free: 114000 bytes
MEMORY USAGE: After running Runner after gc
HEAP: Allocated: 39568 bytes, Free: 126704 bytes
```

### 7 - Runner + Button + Audio:

10 second run (pico W):

```
Running on a microcontroller. Pins are available.
MEMORY USAGE: Before creating Objects before gc
HEAP: Allocated: 32592 bytes, Free: 92784 bytes
MEMORY USAGE: Before creating Objects after gc
HEAP: Allocated: 32528 bytes, Free: 92848 bytes
MEMORY USAGE: Before running Runner before gc
HEAP: Allocated: 68768 bytes, Free: 55360 bytes
MEMORY USAGE: Before running Runner after gc
HEAP: Allocated: 68768 bytes, Free: 55360 bytes
MEMORY USAGE: After running Runner before gc
HEAP: Allocated: 79648 bytes, Free: 44480 bytes
MEMORY USAGE: After running Runner after gc
HEAP: Allocated: 72048 bytes, Free: 52080 bytes
```

10 second run (pico):

```
Running on a microcontroller. Pins are available.
MEMORY USAGE: Before creating Objects before gc
HEAP: Allocated: 33232 bytes, Free: 133040 bytes
MEMORY USAGE: Before creating Objects after gc
HEAP: Allocated: 33168 bytes, Free: 133104 bytes
MEMORY USAGE: Before running Runner before gc
HEAP: Allocated: 69392 bytes, Free: 93424 bytes
MEMORY USAGE: Before running Runner after gc
HEAP: Allocated: 69392 bytes, Free: 93424 bytes
MEMORY USAGE: After running Runner before gc
HEAP: Allocated: 102880 bytes, Free: 59936 bytes
MEMORY USAGE: After running Runner after gc
HEAP: Allocated: 72640 bytes, Free: 90176 bytes
```

### 8 - Runner + Button + Network (full pico-interactive framework):

10 second run (pico W):

```
Running on a microcontroller. Pins are available.
Config file loaded
Connected to WiFi
IP address:  192.168.1.245
CRITICAL - MEMORY USAGE: Before creating Objects before gc
CRITICAL - HEAP: Allocated: 94320 bytes, Free: 29808 bytes
CRITICAL - MEMORY USAGE: Before creating Objects after gc
CRITICAL - HEAP: Allocated: 94288 bytes, Free: 29840 bytes
CRITICAL - MEMORY USAGE: Before running Runner before gc
CRITICAL - HEAP: Allocated: 105024 bytes, Free: 19104 bytes
CRITICAL - MEMORY USAGE: Before running Runner after gc
CRITICAL - HEAP: Allocated: 98304 bytes, Free: 25824 bytes
INFO - Cancelling 2 tasks:
INFO -   <Task>
INFO -   <Task>
ERROR - Caught CancelledError exception for task <closure>
ERROR - Caught CancelledError exception for task <closure>
CRITICAL - MEMORY USAGE: After running Runner before gc
CRITICAL - HEAP: Allocated: 122704 bytes, Free: 1424 bytes
CRITICAL - MEMORY USAGE: After running Runner after gc
CRITICAL - HEAP: Allocated: 101488 bytes, Free: 22640 bytes
```

10 second run (pico):
n/a - no network stack