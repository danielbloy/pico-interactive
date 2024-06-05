# The sensor box has a range of sensors that can be used to send events to the co-ordinator.
import config
import messages
import pico
import coordinator

from picozero import DistanceSensor

import uasyncio as asyncio

import time

# See: https://picozero.readthedocs.io/en/latest/recipes.html#ultrasonic-distance-sensor
DISTANCE_GET = '/distance/get'  # Distance as calculated by an ultrasonic sensor.

MAX_DISTANCE = 4  # Maximum distance of the sensor in meters
ds = DistanceSensor(echo=2, trigger=3, max_distance=MAX_DISTANCE)

PROXIMITY_EVENTS_RESET = '/events/reset'


# Returns the distance of the ultrasonic sensor in cm
async def get_distance():
    distance = ds.distance
    if distance is None:
        distance = ds.max_distance
    return int(distance * 100)


async def send_distance_get_message(ip):
    if config.logging: print("Sending distance message to %s." % ip)
    distance = await get_distance()
    await pico.send_message(ip, "GET", DISTANCE_GET, distance)


async def respond_to_distance_get(method, request, headers, response_headers):
    if config.logging: print("Responding to distance message.")

    distance = await get_distance()

    response_headers[messages.HEADER_CONTENT_TYPE] = messages.CONTENT_TYPE_PLAIN
    response_headers[pico.HEADER_DATA] = str(distance)
    return 'DISTANCE IS %s CM' % distance


# Proximity events are triggered only once within a timeout period
# and this is done using time.
PROXIMITY_EVENT_TIMEOUT = 120
proximity_50 = 0
proximity_100 = 0
proximity_150 = 0
proximity_200 = 0
proximity_250 = 0


async def trigger_event(event):
    if config.logging: print("Triggering event %s." % event)
    if config.coordinator is not None:
        await coordinator.send_event_message(config.coordinator, event)
    else:
        if config.logging: print("Coordinator not set, no event message sent.")


async def check_for_events():
    global proximity_50
    global proximity_100
    global proximity_150
    global proximity_200
    global proximity_250

    distance = await get_distance()
    if config.logging: print("Checking for events based on distance of %s." % distance)

    now = time.time()
    expiry = now + PROXIMITY_EVENT_TIMEOUT

    if distance < 250:
        if proximity_250 < now:
            proximity_250 = expiry
            await trigger_event(coordinator.EVENT_PROXIMITY_250)

        if distance < 200:
            if proximity_200 < now:
                proximity_200 = expiry
                await trigger_event(coordinator.EVENT_PROXIMITY_200)

            if distance < 150:
                if proximity_150 < now:
                    proximity_150 = expiry
                    await trigger_event(coordinator.EVENT_PROXIMITY_150)

                if distance < 100:
                    if proximity_100 < now:
                        proximity_100 = expiry
                        await trigger_event(coordinator.EVENT_PROXIMITY_100)

                    if distance < 50:
                        if proximity_50 < now:
                            proximity_50 = expiry
                            await trigger_event(coordinator.EVENT_PROXIMITY_50)


async def send_proximity_events_reset(ip):
    if config.logging: print("Sending proximity events reset message to %s." % ip)
    await pico.send_message(ip, "GET", PROXIMITY_EVENTS_RESET)


async def respond_to_proximity_events_reset(method, request, headers, response_headers):
    if config.logging: print("Responding to proximity events reset message.")

    global proximity_50
    global proximity_100
    global proximity_150
    global proximity_200
    global proximity_250

    proximity_50 = 0
    proximity_100 = 0
    proximity_150 = 0
    proximity_200 = 0
    proximity_250 = 0

    response_headers[pico.HEADER_DATA] = 'ALL PROXIMITY EVENTS HAVE BEEN RESET'
    return response_headers[pico.HEADER_DATA]


# This must not be too greedy otherwise it will interfere with the HTTP server.
async def background_tasks():
    if config.logging: print("The maximum distance the sensor can return is %s meters." % ds.max_distance)
    while True:
        await asyncio.sleep_ms(50)
        await check_for_events()


def init():
    pico.message_responders[DISTANCE_GET] = respond_to_distance_get
    pico.message_responders[PROXIMITY_EVENTS_RESET] = respond_to_proximity_events_reset


def run():
    init()
    messages.run(background_tasks)
