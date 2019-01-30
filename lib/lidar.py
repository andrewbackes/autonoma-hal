#!/usr/bin/env python3
import Adafruit_GPIO.I2C as I2C
import time


##########################################################################
#  Garmin LIDAR-Lite V3 range finder
##########################################################################
#  - Acquisition time < 0.02s
#  - Power consumption < 100mA
#  - drive power_enable_pin low to save 40mA
#
#  Notes:
#  - Wiring:
#    from pi:
#      red, brown,  black,  white
#      +,   SDA,    SLC,    -
#    from sensor:
#      red,  orange, yellow, green,  blue,   black
#      5v,   enable, mode,   scl,    sda,    ground
#
class Lidar:
    i2c = None

    __ACQ_COMMAND = 0x00
    __STATUS = 0x01
    __SIG_COUNT_VAL = 0x02
    __ACQ_CONFIG_REG = 0x04
    __VELOCITY = 0x09
    __PEAK_CORR = 0x0C
    __NOISE_PEAK = 0x0D
    __SIGNAL_STRENGTH = 0x0E
    __FULL_DELAY_HIGH = 0x0F
    __FULL_DELAY_LOW = 0x10
    __OUTER_LOOP_COUNT = 0x11
    __REF_COUNT_VAL = 0x12
    __LAST_DELAY_HIGH = 0x14
    __LAST_DELAY_LOW = 0x15
    __UNIT_ID_HIGH = 0x16
    __UNIT_ID_LOW = 0x17
    __I2C_ID_HIGHT = 0x18
    __I2C_ID_LOW = 0x19
    __I2C_SEC_ADDR = 0x1A
    __THRESHOLD_BYPASS = 0x1C
    __I2C_CONFIG = 0x1E
    __COMMAND = 0x40
    __MEASURE_DELAY = 0x45
    __PEAK_BCK = 0x4C
    __CORR_DATA = 0x52
    __CORR_DATA_SIGN = 0x53
    __ACQ_SETTINGS = 0x5D
    __POWER_CONTROL = 0x65

    def __init__(self, address=0x62, rate=270):
        self.i2c = I2C.get_i2c_device(address)
        self.rate = rate
        # continuously sample
        self.i2c.write8(self.__OUTER_LOOP_COUNT, 0xFF)

        # Set the sampling frequency as 2000 / Hz:
        # 10Hz = 0xc8
        # 20Hz = 0x64
        # 100Hz = 0x14
        self.i2c.write8(self.__MEASURE_DELAY, int(2000 / rate))

        # Receiver bias correction
        self.i2c.write8(self.__ACQ_COMMAND, 0x04)

        # Acquisition config register:
        # 0x01 Data ready interrupt
        # 0x20 Take sampling rate from MEASURE_DELAY
        self.i2c.write8(self.__ACQ_CONFIG_REG, 0x21)

        # Initial read to start continuous reading
        self._read_delay = 1.0 / rate
        self._last_read = time.time()
        self.read()

    def read(self):
        # Distance is in cm
        # Velocity is in cm between consecutive reads; sampling rate converts
        # these to a velocity.
        dur = time.time() - self._last_read
        if dur < self._read_delay:
            diff = self._read_delay - dur
            time.sleep(diff)
        dist1 = self.i2c.readU8(self.__FULL_DELAY_HIGH)
        dist2 = self.i2c.readU8(self.__FULL_DELAY_LOW)
        self._last_read = time.time()
        distance = ((dist1 << 8) + dist2)
        velocity = -self.i2c.readS8(self.__VELOCITY) * self.rate
        return distance, velocity

    def distance(self):
        d, v = self.read()
        return d

if __name__ == "__main__":
    lidar = Lidar()
    while True:
        print(lidar.read())
        time.sleep(0.5)
