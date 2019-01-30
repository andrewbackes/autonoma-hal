#!/usr/bin/env python3

import time
import os
import pigpio
import RPi.GPIO as GPIO

SG5010 = {
    'secondsPer60deg': 0.19,
    'calibration': {
        'min': 500,
        'max': 2500
    }
}


HD1160A = {
    'secondsPer60deg': 0.12,  # @ 4.8v
    'calibration': {
        'min': 800,
        'max': 2200
    }
}


class Servo:
    _config = {
        'gpio': 37,
        'gpioBCN': 26,
        'frequency': 50,
        'ratio': 1,
        'secondsPer60deg': 0.12,
        'loadCoefficient': 1.25,
        'calibration': {
            'right': 500,
            'left': 2500
        }
    }
    __pos = 0
    __pi = None

    def __init__(self, config=None):
        if config:
            self._config.update(config)
        print("Servo config: ", config)

        self.__pi = pigpio.pi()
        if not self.__pi.connected:
            print("Could not connect to pigpiod.")
            os.exit(1)
        self.__pi.set_mode(self._config['gpioBCN'], pigpio.OUTPUT)
        self.set_position(0)  # move to center position

    def __del__(self):
        self.__pi.stop()

    def __calc_pulse_width(self, deg):
        pos = (self._config['calibration']['left'] -
               self._config['calibration']['right']) / 180
        return pos * (deg + 90) + self._config['calibration']['right']

    def __spin_time(self, deg):
        if deg > self.__pos:
            diff = deg - self.__pos
        else:
            diff = self.__pos - deg
        return ((self._config['secondsPer60deg'] *
                 self._config['loadCoefficient']) * (diff / 60))

    def set_position(self, deg):
        if deg > 75 or deg < -75:
            raise ValueError("Must be between -75 and 75")
        self.__pi.set_servo_pulsewidth(
            self._config['gpioBCN'], self.__calc_pulse_width(deg))
        time.sleep(0.1 + self.__spin_time(deg))
        self.__pi.set_servo_pulsewidth(self._config['gpioBCN'], 0)
        self.__pos = deg

    def position(self):
        return self.__pos


def self_test():
    servo = Servo()
    for p in range(-75, 75, 10):
        print("Position ", p)
        servo.set_position(p)
        time.sleep(0.5)
    del(servo)


def self_test_software_pwm():
    freq = 50
    pin = 37

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin, GPIO.OUT)
    p = GPIO.PWM(pin, freq)

    p.start(1)
    p.ChangeDutyCycle(0.5)
    time.sleep(1)
    p.stop()

    p.start(1)
    p.ChangeDutyCycle(0.25)
    time.sleep(1)
    p.stop()

    p.start(1)
    p.ChangeDutyCycle(0.75)
    time.sleep(1)
    p.stop()

if __name__ == "__main__":
    # self_test_software_pwm()
    self_test()
