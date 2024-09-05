# HTTPServer Library documentation: https://docs.circuitpython.org/projects/httpserver/en/latest/index.html
# API Documentation: https://docs.circuitpython.org/projects/httpserver/en/latest/api.html
#
# Examples of using HTTPServer:
#  * https://learn.adafruit.com/pico-w-http-server-with-circuitpython/code-the-pico-w-http-server
#  * https://learn.adafruit.com/pico-w-wifi-with-circuitpython/pico-w-json-feed-openweathermap
#
# Adafruit requests library:
#  * API Documentation: https://docs.circuitpython.org/projects/requests/en/latest/api.html
#
# The requests library itself:
#  * https://requests.readthedocs.io/en/latest/user/quickstart/

import os
import ssl

from adafruit_httpserver import Server

from environment import is_running_on_microcontroller

# Rather than doing something different based on whether we have pins available or not
# we make the network decision based on whether we are running on a microcontroller or
# not it has a different network stack compared to a desktop.
if is_running_on_microcontroller():
    import wifi
    import socketpool
    import adafruit_requests

    # To set a static IP address
    # import ipaddress
    # ipv4 =  ipaddress.IPv4Address("192.168.1.42")
    # netmask =  ipaddress.IPv4Address("255.255.255.0")
    # gateway =  ipaddress.IPv4Address("192.168.1.1")
    # wifi.radio.set_ipv4_address(ipv4=ipv4,netmask=netmask,gateway=gateway)

    # Connect to the WiFi and setup requests
    wifi.radio.connect(os.getenv('WIFI_SSID'), os.getenv('WIFI_PASSWORD'))
    print("Connected to WiFi")

    pool = socketpool.SocketPool(wifi.radio)
    print("IP address: ", wifi.radio.ipv4_address)

    requests = adafruit_requests.Session(pool, ssl.create_default_context())


else:
    import socket
    import toml
    import requests

    if os.path.isfile('settings.toml'):
        with open('settings.toml') as f:
            config = toml.load(f)

    pool = socket


    def __hide() -> None:
        """This is not expected to be needed but stops PyCharm removing the import"""
        request: requests.Request
        del request


def new_server(debug: bool = False) -> Server:
    return Server(pool, debug=debug)
