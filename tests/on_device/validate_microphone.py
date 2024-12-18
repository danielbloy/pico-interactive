import time

import board
from analogio import AnalogIn

mic_pin = AnalogIn(board.A0)
sampleWindow = 100
ADC_Value = 0


def millis():
    return int(time.monotonic_ns() / 1000000)


divisor = 65535 / 10


def loop():
    startMillis = millis()
    InMax = 0
    InMin = 65535

    while (millis() - startMillis < sampleWindow):
        ADC_Value = mic_pin.value

        if ADC_Value > InMax:
            InMax = ADC_Value
        elif ADC_Value < InMin:
            InMin = ADC_Value

    PeakValue = InMax - InMin
    PeakValue = int(PeakValue / divisor)
    print(f"{PeakValue:3}", "*" * PeakValue)


while True:
    loop()
