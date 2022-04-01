import RPi.GPIO as gpio
import time

gpio.setmode(gpio.BCM)
GPIO_TRIGGER = 18
GPIO_ECHO = 24
gpio.setup(GPIO_TRIGGER, gpio.OUT)
gpio.setup(GPIO_ECHO, gpio.IN)

def distance():
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
    return distance

if __name__ == "__main__":
    print("Finding distance")
    try:
        while True:
            dist = distance()
            print("Distance: %.1f cm" % dist)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDone")
        gpio.cleanup()
