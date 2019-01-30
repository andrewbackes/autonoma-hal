#!/usr/bin/env python3

import time
import RPi.GPIO as gpio

default_config = {
    'echo': 16,
    'trigger': 12
}
'''
sensors = {
    'front' : {
        'echo': 16,
        'trigger': 12 },
    'back' : {
        'echo': 18,
        'trigger': 22 }
}
'''


class UltraSonic:

    def __init__(self, config=default_config):
        self.config = config
        print("Ultrasonic config:", config)
        if gpio.getmode() != gpio.BOARD:
            gpio.setmode(gpio.BOARD)
        gpio.setup(self.config['trigger'], gpio.OUT)
        gpio.setup(self.config['echo'], gpio.IN)

    def distance(self):
        gpio.output(self.config['trigger'], True)
        time.sleep(0.00001)  # specified wait time for this hardware
        gpio.output(self.config['trigger'], False)

        while gpio.input(self.config['echo']) == 0:
            pass

        start = time.time()

        lapsed = time.time() - start
        while gpio.input(self.config['echo']) == 1:
            lapsed = time.time() - start

        distance = (lapsed * 34300) / 2

        return distance


if __name__ == "__main__":
    ultrasonic = UltraSonic()
    while True:
        print("Distance: ", ultrasonic.distance(), 'cm')
        time.sleep(0.5)
