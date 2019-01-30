#!/usr/bin/env python3

import time
import pigpio

default_config = {
    'board': {
        'pwm': {
            'left': 38,
            'right': 40
        },
        'driver': {
            'in4': 7,
            'in3': 11,
            'in2': 13,
            'in1': 15,
        }
    },
    'bcn': {
        'pwm': {
            'left': 20,
            'right': 21
        },
        'driver': {
            'in4': 4,
            'in3': 17,
            'in2': 27,
            'in1': 22,
        }
    }
}


class Move:

    def __init__(self, config=default_config):
        self.config = config
        print("H-bridge config:", config)

        self.__pi = pigpio.pi()
        if not self.__pi.connected:
            print("Could not connect to pigpiod.")
            os.exit(1)

        for pin in self.config['bcn']['pwm'].values():
            self.__pi.set_mode(pin, pigpio.OUTPUT)
        for pin in self.config['bcn']['driver'].values():
            self.__pi.set_mode(pin, pigpio.OUTPUT)

    def __run_at_power(self, t, power=50):
        self.__pi.set_PWM_frequency(self.config['bcn']['pwm']['left'], 100)
        self.__pi.set_PWM_frequency(self.config['bcn']['pwm']['right'], 100)
        self.__pi.set_PWM_dutycycle(self.config['bcn']['pwm'][
                                    'left'], (power / 100) * 255)  # 255 is on
        self.__pi.set_PWM_dutycycle(self.config['bcn']['pwm'][
                                    'right'], (power / 100) * 255)  # 255 is on
        time.sleep(t)
        self.__pi.set_PWM_dutycycle(self.config['bcn']['pwm'][
                                    'left'], 0)
        self.__pi.set_PWM_dutycycle(self.config['bcn']['pwm'][
                                    'right'], 0)

    def __toggle(self, a, b, c, d, t, power=50):
        self.__pi.write(self.config['bcn']['driver']['in4'], a)
        self.__pi.write(self.config['bcn']['driver']['in3'], b)
        self.__pi.write(self.config['bcn']['driver']['in2'], c)
        self.__pi.write(self.config['bcn']['driver']['in1'], d)
        self.__run_at_power(t, power)

    def forward(self, t, power=50):
        print("forward @ " + str(power) + " for t=" + str(t))
        self.__toggle(False, True, True, False, t, power)
        print("movement done")

    def backward(self, t, power=50):
        print("backward @ " + str(power) + " for t=" + str(t))
        self.__toggle(True, False, False, True, t, power)
        print("movement done")

    def turn_left(self, t, power=50):
        self.__toggle(False, True, False, False, t, power)

    def turn_right(self, t, power=50):
        self.__toggle(True, True, True, False, t, power)

    def counter_clockwise(self, t, power=50):
        print("counter_clockwise @ " + str(power) + " for t=" + str(t))
        self.__toggle(False, True, False, True, t, power)
        print("movement done")

    def clockwise(self, t, power=50):
        print("clockwise @ " + str(power) + " for t=" + str(t))
        self.__toggle(True, False, True, False, t, power)
        print("movement done")


if __name__ == "__main__":
    move = Move()
    # move.counter_clockwise(0.1)
    # move.clockwise(0.1)
    move.forward(1, 20)
