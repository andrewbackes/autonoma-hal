#!/usr/bin/env python3

import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008


class IR:

    def distance(self):
        time.sleep(0.05)
        # Hardware SPI configuration:
        # https://www.upgradeindustries.com/product/58/Sharp-10-80cm-Infrared-Distance-Sensor-(GP2Y0A21YK0F)
        # http://www.instructables.com/id/Get-started-with-distance-sensors-and-Arduino/
        SPI_PORT = 0
        SPI_DEVICE = 0
        mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
        value = mcp.read_adc(2)
        cm = 0
        if value:
            cm = 12343.85 * (value**-1.15)
        return cm

if __name__ == "__main__":
    ir = IR()
    while True:
        print(str(ir.distance()) + "cm")
        time.sleep(0.5)
