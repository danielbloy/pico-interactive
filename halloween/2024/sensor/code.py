# Perform import of configuration here to allow for overrides from the config file.
from interactive.configuration import *
from interactive.interactive import Interactive


async def stop_display() -> None:
    pass


async def start_display() -> None:
    pass


async def run_display() -> None:
    pass


config = get_node_config(button=False, buzzer=False)
config.trigger_start = start_display
config.trigger_run = run_display
config.trigger_stop = stop_display

interactive = Interactive(config)


async def callback() -> None:
    pass


interactive.run(callback)
