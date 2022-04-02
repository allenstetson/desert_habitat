"""
desert_habitat.py

This is the main script for the desert habitat, built for Khaleesi the bearded
dragon. It helps to monitor temperature, humidity, and water level, uploading
values to AWS Timestream and visualized on Grafana for AWS. Push notifications
are sent through IFTTT if any abnormal values persist for longer than an
acceptable threshold.

"""
# stdlib
import datetime
import signal
import time

# third party
import adafruit_dht
import board
import decimal
import requests
import RPi.GPIO as gpio

# local
import keys.apikeys
import timestream

# -------------------------------------------------------------------
# HANDLERS
# -------------------------------------------------------------------
def handler(signum, frame):
    """Handles the KeyboardInterrupt signal, cleans up."""
    msg = "\nCntrl+C pressed "
    print(msg)
    gpio.cleanup()
    exit(1)

signal.signal(signal.SIGINT, handler)


# -------------------------------------------------------------------
# GLOBALS
# -------------------------------------------------------------------
DHT_SENSOR1 = adafruit_dht.DHT22(board.D6)
DHT_SENSOR2 = adafruit_dht.DHT22(board.D5)
gpio.setmode(gpio.BCM)
GPIO_TRIGGER = 18
GPIO_ECHO = 24
gpio.setup(GPIO_TRIGGER, gpio.OUT)
gpio.setup(GPIO_ECHO, gpio.IN)


# -------------------------------------------------------------------
# CLASSES
# -------------------------------------------------------------------
class HabitatIot:
    """Class which performs monitoring on all sensors for the habitat.

    The habitat includes two combination humidity/temperature sensors
    (DHT22) and one ultrasonic rangefinder for testing water level.

    Args:
        notify (bool, optional): Whether or not to send push
            notifications upon persistent abnormal readings. Defaults
            to True.
        upload (bool, optional): Whether or not to upload the data to
            AWS (costs are incurred). Defaults to True.
        uploadInterval (int, optional): The number of seconds to wait
            between uploads (in order to reduce costs). Defaults to 600.

    """
    def __init__(self, notify=True, upload=True, uploadInterval=None):
        self.baskingSensor = DHT_SENSOR1
        self.coolingSensor = DHT_SENSOR2
        self.lastAbnormality = datetime.datetime(2007, 2, 7)
        self.lastNotification = datetime.datetime(2012, 12, 1)
        self.lastReadingGood = True
        self.lastUpload = datetime.datetime(2008, 6, 2)
        self.notify = notify
        self.upload = upload
        self.uploadInterval = uploadInterval or 600
        self.writer = timestream.Writer()

    def alertAbnormal(self):
        """Sends a push notification if one hasn't been sent in a while.

        Currently, it is configured to send no more than one push
        notification within 4 hours. Also respects the class variable
        self.notify which is a boolean controlling whether or not
        notifications are sent at all.

        """
        delta = datetime.datetime.now() - self.lastNotification
        if delta.total_seconds()/60/60 > 4.0:
            # it has been more than 4 hours since last notification.
            urlSend = 'https://maker.ifttt.com/trigger/habitat_low_temp/json/with/key/{}'
            urlSend = urlSend.format(keys.apikeys.IFTTT_KEY)
            if not self.notify:
                print("skipping notification as requested.")
                return
            try:
                self.lastNotification = datetime.datetime.now()
                requests.post(urlSend)
                print("Sent request to:\n{}".format(urlSend))
            except requests.exceptions.ConnectionError:
                print("trouble sending notification...")
                print("Notification sent.")
                self.lastNotification = datetime.datetime.now()
        else:
            msg = "Notification was already sent {} hours ago. "
            msg += "Waiting for 4 hours to go by."
            print(msg.format(delta.total_seconds()/60/60))

    def checkValues(self, data):
        """Checks the values for any abnormalities.

        If abnormal readings are detected, this begins tracking whether or not
        abnormal readings have persisted for more than 30 minutes, triggering
        a push notification if so.

        Args:
            data (dict): The data to check for abnormalities.

        """
        abnormalities = []
        if data["baskTemp"] < 75.5:
            abnormalities.append(("Basking Temperature", "low"))
        elif data["baskTemp"] > 102.0:
            abnormalities.append(("Basking Temperature", "high")) 
        if data["coolTemp"] < 68.0:
            abnormalities.append(("Cooling Temperature", "low"))
        elif data["coolTemp"] > 95.0:
            abnormalities.append(("Cooling Temperature", "high")) 
        if data["waterLevel"] < 15.9:
            abnormalities.append(("Water Level", "low")) 

        if abnormalities:
            for abnormality in abnormalities:
                print("ALERT: {} is too {}!".format(abnormality[0], abnormality[1]))
            if self.lastReadingGood:
                self.lastReadingGood = False
                self.lastAbnormality = datetime.datetime.now()
                print("First abnormal reading detected.")
                return
            delta = datetime.datetime.now() - self.lastAbnormality
            if delta.total_seconds()/60 > 30:
                # abnormality has persisted for more than 30 mins!
                print("Persistent abnormal readings! Notifying.")

                self.alertAbnormal()
                return
            print("Subsequent abnormal reading; waiting until 30m is up.")
            return
        self.lastReadingGood = True

    def gatherData(self, i=0):
        """Reads the sensors to gather the data from them.

        Returns:
            dict: The dictionary of values that were read from sensors within
                the habitat.

        """
        try:
            # Sensor prone to partial buffer error; retry loop:
            humidity1 = self.baskingSensor.humidity
            tempC1 = self.baskingSensor.temperature
            # -
            humidity2 = self.coolingSensor.humidity
            tempC2 = self.coolingSensor.temperature
        except RuntimeError:
            if i == 20:
                print("ALERT: Sensor is unreachable!")
                self.alertAbnormal()
                raise
            i += 1
            print("Nope. Retrying")
            time.sleep(0.25)
            return self.gatherData(i=i)
        tempF1 = tempC1 * (9/5) + 32
        print("basking humidity: {}%".format(humidity1))
        print("basking temperature: {} c ({} f)".format(tempC1, tempF1))
        # -
        tempF2 = tempC2 * (9/5) + 32
        print("cooling humidity: {}%".format(humidity2))
        print("cooling temperature: {} c ({} f)".format(tempC2, tempF2))
        data = {
            "baskTemp": tempF1,
            "baskHumidity": humidity1,
            "coolTemp": tempF2,
            "coolHumidity": humidity2
        }
        return data

    def gatherWaterLevel(self):
        """Pings the water level as distance in cm from ultrasonic rangefinder.

        Returns:
            float: The distance in centimeters from the rangefinder.

        """
        gpio.output(GPIO_TRIGGER, True)
        # one millisecond ping
        time.sleep(.00001)
        gpio.output(GPIO_TRIGGER, False)

        startTime = time.time()
        stopTime = time.time()
        while gpio.input(GPIO_ECHO) == 0:
            startTime = time.time()
        while gpio.input(GPIO_ECHO) == 1:
            stopTime = time.time()

        elapsed = stopTime - startTime
        distance = (elapsed * 34300) / 2
        if distance < 0:
            # Negative value resulting from sensor error
            print("ERROR reading water level, trying again")
            time.sleep(0.5)
            return gatherWaterLevel()
        distance = float(decimal.Decimal(distance).quantize(decimal.Decimal('.1')))
        #-
        full = 3.0
        empty = 9.0
        percEmpty = (100 / empty - full) * (distance - full)
        percFull = 100.0 - percEmpty
        percFull = float(decimal.Decimal(percFull).quantize(decimal.Decimal('.1')))
        #-
        print("Water level is {} cm from sensor ({}% full)".format(distance, percFull))
        return percFull

    def run(self):
        """Main workhorse that continually reads data, checks it, and reports.

        This runs in a continual loop until the user interrupts it with a
        Cntrl+C KeyboardInterrupt.

        """
        while True:
            msg = "---------  {}  ---------"
            msg = msg.format(
                datetime.datetime.now().strftime("%Y.%m.%d - %H:%M:%S")
            )
            print(msg)
            data = self.gatherData()
            waterLevel = self.gatherWaterLevel()
            data["waterLevel"] = waterLevel
            self.checkValues(data)
            if self.upload:
                uploadDelta = datetime.datetime.now() - self.lastUpload
                if uploadDelta > datetime.timedelta(seconds=self.uploadInterval):
                    self.uploadData(data)
                    self.lastUpload = datetime.datetime.now()
                else:
                    print("waiting for upload interval ({} seconds)".format(self.uploadInterval))
            time.sleep(30)

    def uploadData(self, data):
        """Uploads sensor data to AWS Timestream.

        Args:
            data (dict): Dictionary of values that were read from sensors
                within the habitat.

        """
        self.writer.writeRecords(
            data["baskTemp"],
            data["coolTemp"],
            data["baskHumidity"],
            data["coolHumidity"],
            data["waterLevel"]
        )


# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------
if __name__ == "__main__":
    try:
        habitatIot = HabitatIot(notify=False, upload=True)
        habitatIot.run()
    except KeyboardInterrupt:
        print("\nDone")
