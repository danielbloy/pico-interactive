from adafruit_httpserver import Request, Response, Server, Route, GET


# @server.route("/")
def base(request: Request):
    """

    Serve a default static plain text message.

    """

    return Response(request, "Hello from the CircuitPython HTTP Server!")


# Ports below 1024 are reserved for root user only.

# If you want to run this example on a port below 1024, you need to run it as root (or with `sudo`).


# server = new_server()


import socket

pool = socket
pool.timeout(1)

server = Server(pool, "/static", debug=True)
server.socket_timeout = 3
server.add_routes([
    Route("/help", GET, base),
])

server.serve_forever("127.0.0.1", 5001)

# With debug=True, there will be lots of errors in Windows about a non-blocking operation.
# These are harmless but can be turned off by either disabling debug or changing:
#   sock.setblocking(False)  # Non-blocking socket
#
# To:
#   sock.setblocking(True)  # Non-blocking socket
#
# On line 211 in adafruit_httpserver/server.py
