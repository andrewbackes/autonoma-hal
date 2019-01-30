#!/usr/bin/env python3

import time
import sys
import RPi.GPIO as gpio

#
# Nema 17
#
#  - Coil #1: Red & Yellow wire pair. Coil #2 Green & Brown/Gray wire pair.
#  - Datasheet:
#       https://cdn-shop.adafruit.com/product-files/324/C140-A+datasheet.jpg
#


class Stepper:

    CLOCKWISE = 0
    COUNTER_CLOCKWISE = 1

    _config = {
        "gpio": {
            "step":     36,
            "dir":      32,
            "ms1":      16,  # GPIO-23
            "ms2":      22,  # GPIO-25
            "ms3":      18,  # GPIO-24
            "enable":   12   # GPIO-18
        },

        # without micro-stepping:
        "stepsPerRevolution": 200,  # 1.8 per step
        "stepDelay": 1.0 / 200,

        # micro-stepping:
        "microstepping": 1 / 16,
        "resolution_map": {
            #        MS1,          MS2,           MS3
            1:      (gpio.LOW,     gpio.LOW,      gpio.LOW),
            1 / 2:  (gpio.HIGH,    gpio.LOW,      gpio.LOW),
            1 / 4:  (gpio.LOW,     gpio.HIGH,     gpio.LOW),
            1 / 8:  (gpio.HIGH,    gpio.HIGH,     gpio.LOW),
            1 / 16: (gpio.HIGH,    gpio.HIGH,     gpio.HIGH),
        },
    }

    def __init__(self, config={}):
        self._config.update(config)
        if gpio.getmode() != gpio.BOARD:
            gpio.setmode(gpio.BOARD)
        gpio.setup(self._config['gpio']['dir'], gpio.OUT)
        gpio.setup(self._config['gpio']['step'], gpio.OUT)
        gpio.setup(self._config['gpio']['enable'], gpio.OUT)
        self.set_direction(self.CLOCKWISE)

        # adjust for micro-stepping:
        self._stepsPerRevolution = int(self._config[
            'stepsPerRevolution'] / self._config['microstepping'])
        self._stepDelay = 1.0 / self._stepsPerRevolution
        self._mode = (
            self._config['gpio']['ms1'],
            self._config['gpio']['ms2'],
            self._config['gpio']['ms3']
        )
        gpio.setup(self._mode, gpio.OUT)
        gpio.output(self._mode, self._config['resolution_map'][
                    self._config['microstepping']])

        # for tracking:
        self._steps = 0
        self._degrees_per_step = (1.0 / self._stepsPerRevolution) * 360

        # logging:
        print('Stepper values: ', {
            '_stepsPerRevolution': self. _stepsPerRevolution,
            '_stepDelay': self._stepDelay,
            '_direction': self.__direction,
            '_steps': self._steps,
        })

    def enable(self):
        gpio.output(self._config['gpio']['enable'], gpio.LOW)

    def disable(self):
        gpio.output(self._config['gpio']['enable'], gpio.HIGH)

    def set_direction(self, dir):
        if dir != self.CLOCKWISE and dir != self.COUNTER_CLOCKWISE:
            raise ValueError('dir must be 0 or 1')
        self.__direction = dir
        gpio.output(self._config['gpio']['dir'], dir)

    def direction(self):
        return self.__direction

    def step(self, number=1):
        for x in range(number):
            gpio.output(self._config['gpio']['step'], gpio.HIGH)
            time.sleep(self._stepDelay)
            gpio.output(self._config['gpio']['step'], gpio.LOW)
            time.sleep(self._stepDelay)
        if self.direction() == self.CLOCKWISE:
            delta = number
        else:
            delta = -number
        self._steps = (self._steps + delta) % self._stepsPerRevolution

    def home(self):
        '''Set stepper to home position'''
        while self._steps % self._stepsPerRevolution != 0:
            self.step()

    def set_position(self, degrees):
        '''Move to a position in degrees'''
        if degrees > 0:
            target = (degrees % 360)
        else:
            target = (degrees % 360) + 360
        while self.position() >= target + self._degrees_per_step \
                or self.position() <= target - self._degrees_per_step:
            self.step()

    def position(self):
        '''Position in degrees from 'home' position'''
        pos = ((self._steps % self._stepsPerRevolution) /
               self._stepsPerRevolution) * 360
        if pos < 0:
            pos = pos + 360
        return pos


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--disable':
        stepper = Stepper()
        stepper.disable()
        print("Stepper disabled")
        return
    print("Stepper test")
    stepper = Stepper()
    stepper.enable()
    try:
        while True:
            stepper.step(self._stepsPerRevolution)
    except:
        pass
    stepper.disable()
    gpio.cleanup()

if __name__ == "__main__":
    main()
