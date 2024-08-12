# TODO: See here: https://docs.circuitpython.org/projects/httpserver/en/latest/index.html
# TODO: From this example: https://learn.adafruit.com/pico-w-http-server-with-circuitpython/code-the-pico-w-http-server
# Look to support setting of IP Address.
# https://learn.adafruit.com/pico-w-wifi-with-circuitpython/pico-w-json-feed-openweathermap

import os
import ssl

from adafruit_httpserver import Server, Request, Response

from interactive.environment import are_pins_available


def __hide() -> None:
    """This is not expected to be needed but stops PyCharm removing the import"""
    server: Server
    request: Request
    response: Response
    del server
    del request
    del response


if are_pins_available():
    import wifi
    import socketpool
    import adafruit_requests

    # TODO: from adafruit_httpserver import Server, Request, Response, POST

    #  set static IP address
    # ipv4 =  ipaddress.IPv4Address("192.168.1.42")
    # netmask =  ipaddress.IPv4Address("255.255.255.0")
    # gateway =  ipaddress.IPv4Address("192.168.1.1")
    # wifi.radio.set_ipv4_address(ipv4=ipv4,netmask=netmask,gateway=gateway)
    #  connect to your SSID

    # Connect to the WiFi and setup requests
    wifi.radio.connect(os.getenv('CIRCUITPY_WIFI_SSID'), os.getenv('CIRCUITPY_WIFI_PASSWORD'))
    print("Connected to WiFi")

    pool = socketpool.SocketPool(wifi.radio)
    print("IP address: ", wifi.radio.ipv4_address)

    requests = adafruit_requests.Session(pool, ssl.create_default_context())


else:
    import socket
    import toml

    with open('settings.toml') as f:
        config = toml.load(f)

    pool = socket


def new_server() -> Server:
    return Server(pool, "/static", debug=True)
