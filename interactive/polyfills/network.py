import os
import ssl

from interactive.environment import are_pins_available

# TODO: From this example: https://learn.adafruit.com/pico-w-http-server-with-circuitpython/code-the-pico-w-http-server
# Look to support setting of IP Address.


if are_pins_available():
    import wifi
    import socketpool
    import adafruit_requests

    # Connect to the WiFi and setup requests
    wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
    print("Connected to WiFi")

    pool = socketpool.SocketPool(wifi.radio)
    print("IP address: ", wifi.radio.ipv4_address)

    requests = adafruit_requests.Session(pool, ssl.create_default_context())
else:
    import requests
    import toml

    with open('settings.toml') as f:
        config = toml.load(f)


    def __hide() -> None:
        """This is not expected to be needed but stops PyCharm removing the import"""
        request: requests.Request
        del request
