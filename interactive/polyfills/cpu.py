from interactive.environment import is_running_on_microcontroller

if is_running_on_microcontroller():

    import gc
    import microcontroller


    def __cpu_info():
        return {
            "temperature": microcontroller.cpu.temperature,
            "frequency": microcontroller.cpu.frequency,
            "voltage": microcontroller.cpu.voltage,
            "heap bytes used": gc.mem_alloc(),
            "head bytes free": gc.mem_free(),
        }


    def __cpu_restart():
        import microcontroller
        microcontroller.reset()

else:

    def __cpu_info():
        return {
            "temperature": "n/a",
            "frequency": "n/a",
            "voltage": "n/a",
            "heap bytes free": "n/a",
            "head bytes used": "n/a",
        }


    def __cpu_restart():
        pass


def info():
    """
    Returns some basic information about the state of the CPU.
    """
    return __cpu_info()


def restart():
    """
    Reboots the microcontroller; does nothing for a non-microcontroller.
    """
    __cpu_restart()
