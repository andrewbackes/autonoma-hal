# Autonoma-HAL
Hardware Abstraction Layer

This project is designed to provide abstraction over the bot's hardware. The hardware being the motors, sensors, etc. To communication with the hardware abstraction layer, you send commands in json format over TCP. In this way the control and perception layers do not have to be on the bot. Of course, that comes at the cost of network latency and json deserialization.

It is written to run on a Raspberry Pi running Raspian. Sensors/motors are controlled via GPIO, I2C, SPI, etc.

## Usage
Make sure `pigpiod` is running.

This is a python3 project. It has two running modes, which can be controlled via command line flags: `--manual` and `--network`. When in manual mode the bot can be controlled with keyboard input. When in network mode it will await a TCP connection. It expects JSON commands to tell it what to do.

## Supported Hardware
Right now there are abstractions for:
- Sharp IR Distance Sensor (10-80cm)
- MCP3008 8-Channel 10-Bit ADC With SPI Interface
- Garmin LIDAR-Lite V3 Range Finder
- Motor H-Bridges
- Adafruit BNO055 Absolute Orientation Sensor
- Stepper Motors
- Servos (SG5010 and HD1160A)
- HC-SR04 Ultrasonic Sensor
