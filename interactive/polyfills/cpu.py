from interactive.environment import is_running_on_microcontroller

if is_running_on_microcontroller():

    import microcontroller


    def __cpu_info():
        return {
            "temperature": microcontroller.cpu.temperature,
            "frequency": microcontroller.cpu.frequency,
            "voltage": microcontroller.cpu.voltage,
        }

else:

    def __cpu_info():
        return {
            "temperature": "n/a",
            "frequency": "n/a",
            "voltage": "n/a",
        }


def cpu_info():
    """
    Returns some basic information about the state of the CPU.
    """
    return __cpu_info()
