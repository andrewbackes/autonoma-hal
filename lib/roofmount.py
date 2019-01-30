#!/usr/bin/env python3

import time

from lib.stepper import Stepper
from lib.servo import Servo

from lib.lidar import Lidar


class RoofMount:

    _config = {
        'servo': {
            'enabled': True,
            # for calibration
            'level_degrees': 35,
            'max_degrees': 70,   # down
            'min_degrees': -48,  # up
        },
        'lidar': {
            'enabled': True,
            'updateRatePerSecond': 270
        }
    }

    def __init__(self, config={}):
        self._config.update(config)
        self._stepper = Stepper()
        self._stepper.disable()
        self._servo = Servo()
        self.set_vertical_position(0)
        self._lidar = Lidar()

    def up(self, degrees=10):
        '''Move up relative to current position'''
        try:
            self._servo.set_position(self._servo.position - degrees)
        except:
            pass

    def down(self, degrees=10):
        '''Move down relative to current position'''
        try:
            self._servo.set_position(self._servo.position + degrees)
        except:
            pass

    def level(self):
        '''Vertically level the mount'''
        self._servo.set_position(self._config['servo']['level_degrees'])

    def clockwise(self, degrees=10):
        '''Move clockwise relative to current position'''
        self.__rotate(Stepper.CLOCKWISE,
                      (self._stepper.position() + degrees) % 360)

    def counter_clockwise(self, degrees=10):
        '''Move counter-clockwise relative to current position'''
        self.__rotate(Stepper.COUNTER_CLOCKWISE,
                      (self._stepper.position() - degrees) % 360)

    def __rotate(self, dir, degrees):
        self._stepper.enable()
        self._stepper.set_direction(dir)
        self._stepper.set_position(degrees)
        self._stepper.disable()

    def home(self):
        '''Move stepper and servo to home positions'''
        self._stepper.home()
        self.level()

    def horizontal_position(self):
        return self._stepper.position()

    def vertical_position(self):
        return self._config['servo']['level_degrees'] - self._servo.position()

    def set_horizontal_position(self, degrees):
        '''Take shortest path to target degrees'''
        diff = degrees - self._stepper.position()
        if diff < 0:
            diff += 360
        if diff <= 180:
            self.__rotate(Stepper.CLOCKWISE, degrees)
        else:
            self.__rotate(Stepper.COUNTER_CLOCKWISE, degrees)

    def set_vertical_position(self, degrees):
        '''Position relative to the horizon'''
        min = -(self._config['servo']['max_degrees'] -
                self._config['servo']['level_degrees'])
        max = -(self._config['servo']['min_degrees'] -
                self._config['servo']['level_degrees'])
        if degrees < min or degrees > max:
            print('Position ', degrees,
                  'out of range (', min, ',', max, ')')
            return
        pos = -degrees + self._config['servo']['level_degrees']
        self._servo.set_position(pos)

    def get_readings(self):
        return {
            'vertical_position': self.vertical_position(),
            'horizontal_position': self.horizontal_position(),
            'lidar': self._lidar.distance(),
        }

    def horizontal_scan(self, vertical_degrees, resolution=1.0, callback=None):
        '''Performs a 360 scan at a specified angle. Resolution is a
        percentage and dictates how often a readings is performed during
        the scan.'''
        print("Performing scan.")
        readings = []
        self.set_vertical_position(vertical_degrees)
        self._stepper.enable()
        for step in range(self._stepper._stepsPerRevolution):
            self._stepper.step()
            if step % (1 / resolution) == 0:
                reading = self.get_readings()
                readings.append(reading)
                if callback is not None:
                    callback(reading)
        self._stepper.disable()
        return readings


def self_test():
    print("Roof mount self test.")
    roofmount = RoofMount()
    # Test 1
    print("Testing vertical movement...")
    roofmount.set_vertical_position(83)
    roofmount.set_vertical_position(0)
    roofmount.set_vertical_position(-35)
    print("Done.")

    # Test 2
    print("Clockwise downward rotation....")
    roofmount.set_vertical_position(-35)
    for degrees in range(36):
        roofmount.clockwise(10)
    print("Done.")

    # Test 3
    print("Counter-clockwise level rotation....")
    roofmount.set_vertical_position(0)
    for degrees in range(36):
        roofmount.counter_clockwise(10)
    print("Done.")

    # Test 4
    print("Full clockwise upward rotation....")
    roofmount.set_vertical_position(83)
    for degrees in range(36):
        roofmount.clockwise(10)
    print("Done.")
    roofmount.set_vertical_position(0)

if __name__ == "__main__":
    self_test()
