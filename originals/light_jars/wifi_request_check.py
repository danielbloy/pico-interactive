import time
from network import requests

#  adafruit quotes URL
quotes_url = "https://www.adafruit.com/api/quotes.php"


while True:
    try:
        #  pings adafruit quotes
        print("Fetching text from %s" % quotes_url)
        #  gets the quote from adafruit quotes
        response = requests.get(quotes_url)
        print("-" * 40)
        #  prints the response to the REPL
        print("Text Response: ", response.text)
        print("-" * 40)
        response.close()
        #  delays for 1 minute
        time.sleep(60)
    # pylint: disable=broad-except
    except Exception as e:
        import microcontroller

        print("Error:\n", str(e))
        print("Resetting microcontroller in 10 seconds")
        time.sleep(10)
        microcontroller.reset()
