#!/usr/bin/env python3

from Adafruit_BNO055 import BNO055
import time


class Orientation:

    def __init__(self):
        # use i2c by not passing arg in constructor
        self.bno055 = BNO055.BNO055()
        if not self.bno055.begin():
            raise RuntimeError(
                'Failed to initialize BNO055! Is the sensor connected?')
        self.__self_test()

    def __self_test(self):
        print('Running BNO055 self test')
        # Print system status and self test result.
        status, self_test, error = self.bno055.get_system_status()
        print('System status: {0}'.format(status))
        print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
        # Print out an error if system status is in error mode.
        if status == 0x01:
            print('System error: {0}'.format(error))
            print('See datasheet section 4.3.59 for the meaning.')
        sw, bl, accel, mag, gyro = self.bno055.get_revision()
        print('Software version:   {0}'.format(sw))
        print('Bootloader version: {0}'.format(bl))
        print('Accelerometer ID:   0x{0:02X}'.format(accel))
        print('Magnetometer ID:    0x{0:02X}'.format(mag))
        print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))

    def read(self):
        time.sleep(0.01)
        # heading, roll, pitch = self.bno055.read_euler()
        # sys, gyro, accel, mag = self.bno055.get_calibration_status()
        return self.bno055.read_euler(), self.bno055.get_calibration_status()

    def euler(self):
        time.sleep(0.01)
        euler, cal = self.read()
        # heading, roll, pitch = euler
        return euler


if __name__ == "__main__":
    orientation = Orientation()
    while True:
        print(orientation.read())
        time.sleep(1)

    # Other values you can optionally read:
    # Orientation as a quaternion:
    # x,y,z,w = bno.read_quaterion()
    # Sensor temperature in degrees Celsius:
    # temp_c = bno.read_temp()
    # Magnetometer data (in micro-Teslas):
    # x,y,z = bno.read_magnetometer()
    # Gyroscope data (in degrees per second):
    # x,y,z = bno.read_gyroscope()
    # Accelerometer data (in meters per second squared):
    # x,y,z = bno.read_accelerometer()
    # Linear acceleration data (i.e. acceleration from movement, not gravity--
    # returned in meters per second squared):
    # x,y,z = bno.read_linear_acceleration()
    # Gravity acceleration data (i.e. acceleration just from gravity--returned
    # in meters per second squared):
    # x,y,z = bno.read_gravity()
    # Sleep for a second until the next reading.
