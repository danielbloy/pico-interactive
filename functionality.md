# Functionality

* [x] Add generic task runner that handles both completion and exceptions and support restarts.
    * [x] Works on CircuitPython
    * [x] Works with Blinka
* [x] Add support for logging in both Desktop and Pico environments.
    * [x] Works on CircuitPython
    * [x] Works with Blinka
* [x] Add button support for single, double and long-presses.
    * [x] Works on CircuitPython
    * [x] Works with Blinka
* [x] Add buzzer support for playing tones.
    * [x] Works on CircuitPython
    * [x] Works with Blinka
* [x] Migrate music.py/Song from originals/christmas to buzzer.py as Melody
    * [ ] Write tests
* [x] Migrate music.py/SongSequence from originals/christmas to buzzer.py as MelodySequence
    * [ ] Write tests
* [x] Add NeoPixel support
    * [x] Works on CircuitPython
    * [x] Works with Blinka
* [x] Migrate Flicker from originals/christmas and originals/light_jars to pixel.py
    * [ ] Add tests for Flicker
* [ ] Add a Flame effect for pixels
    * [ ] Add tests for Flame
* [ ] Add a Lightning effect for pixels
    * [ ] Add tests for Lightning
* [x] Add LED support
    * [x] Works on CircuitPython
    * [x] Works with Blinka
* [x] Add Ultrasonic sensor support
    * [x] Works on CircuitPython
    * [ ] ~~Works with Blinka~~ Blinka is too slow on PC
* [x] Add Audio support
    * [x] Works on CircuitPython
    * [ ] ~~Works with Blinka~~ Blinka is too slow on PC
* [x] Add Wi-Fi support
    * [x] Works on CircuitPython
    * [x] Works with Blinka
* [x] Add support for network node information page: index, inspect, cpu-information
* [x] Add support for standard messages: alive, name, role, blink, led on/off, restart, trigger
* [x] Add support for network directory via coordinator node (PC/Raspberry Pi) (register/unregister, heartbeat etc.)
* [ ] Add current time of day support via Wi-Fi
    * [ ] Works on CircuitPython
    * [ ] Works with Blinka
* [ ] Trigger message should accept JSON data.
* [ ] Add in a directory-information route to export as JSON data about the directory.
* [ ] Improve the '/' and '/inspect' routes with more information and better formatting.
* [ ] Add in a node-information route to return the node information as JSON.
* [ ] Migrate to a lighter weight, faster and async HTTP server stack such
  as [Biplane](https://github.com/Uberi/biplane).
* [ ] Add Servo support
    * [ ] Works on CircuitPython
    * [ ] Works with Blinka
* [ ] Add Motor support
    * [ ] Works on CircuitPython
    * [ ] Works with Blinka
* [ ] Add UART support
    * [ ] Works on CircuitPython
    * [ ] Works with Blinka
* [ ] Add I2S audio support
    * [ ] Works on CircuitPython
    * [ ] Works with Blinka
* [ ] Add DFPlayer Pro audio support
    * [ ] Works on CircuitPython
    * [ ] Works with Blinka
* [ ] Add OLED/TFT screen support
    * [ ] Works on CircuitPython
    * [ ] Works with Blinka
* [ ] Embed pico-interactive version number in library based on release.
* [ ] Make a pico-interactive release (
  see [Creating and sharing a CircuitPython library](https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library?view=all#mpy-2982472-11)):
    * [ ] Compile to`.mpy` files