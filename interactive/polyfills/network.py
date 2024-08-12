import os
import ssl

from interactive.environment import are_pins_available

# TODO: See here: https://docs.circuitpython.org/projects/httpserver/en/latest/index.html
# TODO: From this example: https://learn.adafruit.com/pico-w-http-server-with-circuitpython/code-the-pico-w-http-server
# Look to support setting of IP Address.
# https://learn.adafruit.com/pico-w-wifi-with-circuitpython/pico-w-json-feed-openweathermap

if are_pins_available():
    import wifi
    import socketpool
    import adafruit_requests
    from adafruit_httpserver import Server, Request

    import ipaddress

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
    import requests
    import toml
    from http import server as Server, server

    # TODO may not need this. from requests import Request, Response

    with open('settings.toml') as f:
        config = toml.load(f)


    def __hide() -> None:
        """This is not expected to be needed but stops PyCharm removing the import"""
        server: Server
        request: requests.Request
        # response: requests.Response TODO
        del server
        del request
        # del response TODO


#  route default static IP
@server.route("/")
def base(request: Request):  # pylint: disable=unused-argument
    #  serve the HTML f string
    #  with content type text/html
    return requests.Response(request, f"{webpage()}", content_type='text/html')


#  if a button is pressed on the site
@server.route("/", requests.POST)
def buttonpress(request: Request):
    #  get the raw text
    raw_text = request.raw_request.decode("utf8")
    print(raw_text)
    #  if the led on button was pressed
    if "ON" in raw_text:
        #  turn on the onboard LED
        print("turn LED on")
    #  reload site
    return requests.Response(request, f"{webpage()}", content_type='text/html')


# TODO: Remove
font_family = "monospace"
temp_test = "BLAH"
unit = "F"


def webpage():
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta http-equiv="Content-type" content="text/html;charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
    html{{font-family: {font_family}; background-color: lightgrey;
    display:inline-block; margin: 0px auto; text-align: center;}}
      h1{{color: deeppink; width: 200; word-wrap: break-word; padding: 2vh; font-size: 35px;}}
      p{{font-size: 1.5rem; width: 200; word-wrap: break-word;}}
      .button{{font-family: {font_family};display: inline-block;
      background-color: black; border: none;
      border-radius: 4px; color: white; padding: 16px 40px;
      text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}}
      p.dotted {{margin: auto;
      width: 75%; font-size: 25px; text-align: center;}}
    </style>
    </head>
    <body>
    <title>Pico W HTTP Server</title>
    <h1>Pico W HTTP Server</h1>
    <br>
    <p class="dotted">This is a Pico W running an HTTP server with CircuitPython.</p>
    <br>
    <p class="dotted">The current ambient temperature near the Pico W is
    <span style="color: deeppink;">{temp_test:.2f}°{unit}</span></p><br>
    <h1>Control the LED on the Pico W with these buttons:</h1><br>
    <form accept-charset="utf-8" method="POST">
    <button class="button" name="LED ON" value="ON" type="submit">LED ON</button></a></p></form>
    <p><form accept-charset="utf-8" method="POST">
    <button class="button" name="LED OFF" value="OFF" type="submit">LED OFF</button></a></p></form>
    <h1>Party?</h>
    <p><form accept-charset="utf-8" method="POST">
    <button class="button" name="party" value="party" type="submit">PARTY!</button></a></p></form>
    </body></html>
    """
    return html


# TODO: Sample code to pull out.
quotes_url = "https://www.adafruit.com/api/quotes.php"
response = requests.get(quotes_url)
print("Text Response: ", response.text)
print("-" * 40)
response.close()

server = Server(pool, "/static", debug=True)

try:
    server.start(str(wifi.radio.ipv4_address))
    print("Listening on http://%s:80" % wifi.radio.ipv4_address)
#  if the server fails to begin, restart the pico w
except OSError:
    print("Failed to start network")

while True:
    try:
        ping_address = ipaddress.ip_address("8.8.4.4")

        if wifi.radio.ping(ping_address) is None:
            print("lost connection")
        else:
            print("Connected to:")

        server.poll()

    except Exception as e:
        print(e)
        continue
