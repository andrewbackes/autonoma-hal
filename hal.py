#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import RPi.GPIO as gpio
from lib.orientation import Orientation
from lib.move import Move
from lib.roofmount import RoofMount
from lib.ir import IR
from lib.ultrasonic import UltraSonic

from util.getch import *
from util.tcp import TCP

import json
import sys
import os
import time


class Bot:
    _config = {
        "hbridge": {"enabled": False},
        "roofmount": {"enabled": False},
        "orientation": {"enabled": False},
    }
    _move = None
    _roofmount = None
    _orientation = None

    def __init__(self, config):
        print("Initializing Hardware Abstraction Layer...")
        gpio.setmode(gpio.BOARD)
        self._config.update(config)
        # controls:
        if self._config['hbridge'] and self._config['hbridge']['enabled']:
            self._move = Move()
        if self._config['roofmount'] and self._config['roofmount']['enabled']:
            self._roofmount = RoofMount(self._config['roofmount'])
        # orientation:
        if self._config['orientation'] \
                and self._config['orientation']['enabled']:
            self.orientation = Orientation()

    def __del__(self):
        print("done")
        gpio.cleanup()

    def get_readings(self):
        r = {}
        if self._roofmount is not None:
            r.update(self._roofmount.get_readings())
        r['timestamp'] = time.time()
        return json.dumps(r)

    def get_orientation(self):
        r = {}
        if self.orientation is not None:
            yaw, roll, pitch = self.orientation.euler()
            r = {
                'yaw': yaw,
                'roll': roll,
                'pitch': pitch
            }
        return json.dumps(r)

    def manual_control(self):
        print("Use w,a,s,d to move the vehicle. to exit")
        t = 0.2
        speed = 50
        step = 10
        while True:
            print(self.get_readings())
            print('Speed ', speed)
            k = getch()
            cmd = None
            if k == "w":
                cmd = {'command': 'move', 'direction': 'forward',
                       'speed': speed, 'time': t}
            elif k == "s":
                cmd = {'command': 'move', 'direction': 'backward',
                       'speed': speed, 'time': t}
            elif k == "a":
                cmd = {'command': 'move', 'direction': 'counter_clockwise',
                       'speed': speed, 'time': t}
            elif k == "d":
                cmd = {'command': 'move', 'direction': 'clockwise',
                       'speed': speed, 'time': t}
            elif k == 't':
                speed = min(100, speed + step)
            elif k == 'g':
                speed = max(0, speed - step)
            elif k == "q" and self._roofmount is not None:
                cmd = {'command': 'horizontal_position',
                       'position': (self._roofmount.horizontal_position() +
                                    (360 - 15)) % 360}
            elif k == "e" and self._roofmount is not None:
                cmd = {'command': 'horizontal_position',
                       'position': (self._roofmount.horizontal_position() +
                                    15) % 360}
            elif k == "r" and self._roofmount is not None:
                cmd = {'command': 'vertical_position',
                       'position': self._roofmount.vertical_position() + 15}
            elif k == "f" and self._roofmount is not None:
                cmd = {'command': 'vertical_position',
                       'position': self._roofmount.vertical_position() - 15}
            elif k == 'z' and self._roofmount is not None:
                cmd = {'command': 'horizontal_scan', 'vertical_position':
                       self._roofmount.vertical_position(), 'resolution': 1.0}
            elif k == 'p':
                continue
            elif k == "x":
                break
            if cmd is not None:
                self.__execute(cmd)

    def network_control(self):
        self.tcp = TCP()
        self.tcp.listen(self.__handler)

    def __handler(self, payload):
        print('Handling ' + payload)
        try:
            cmd = json.loads(payload)
        except:
            print("Could not decode json")
            return
        self.__execute(cmd)

    def __execute(self, cmd):
        # Drive controls:
        if cmd['command'] == 'move' and cmd['direction'] == 'forward':
            if self._move:
                self._move.forward(cmd['time'], cmd['speed'])
        elif cmd['command'] == 'move' and cmd['direction'] == 'backward':
            if self._move:
                self._move.backward(cmd['time'], cmd['speed'])
        elif cmd['command'] == 'move' \
                and cmd['direction'] == 'counter_clockwise':
            if self._move:
                self._move.counter_clockwise(
                    cmd['time'], cmd['speed'])
        elif cmd['command'] == 'move' and cmd['direction'] == 'clockwise':
            if self._move:
                self._move.clockwise(cmd['time'], cmd['speed'])

        # View controls:
        elif cmd['command'] == 'horizontal_position':
            if self._roofmount:
                self._roofmount.set_horizontal_position(cmd['position'])
        elif cmd['command'] == 'vertical_position':
            if self._roofmount:
                self._roofmount.set_vertical_position(cmd['position'])

        # Sensor controls:
        elif cmd['command'] == 'get_orientation':
            self.tcp.send(self.get_orientation())
        elif cmd['command'] == 'get_readings':
            self.tcp.send(self.get_readings())
        elif cmd['command'] == 'horizontal_scan':
            readings = self._roofmount.horizontal_scan(
                cmd['vertical_position'],
                cmd['resolution'],
                lambda reading: self.tcp.send(json.dumps(reading)))
            self.tcp.send(json.dumps(
                '{"command": "horizontal_scan", "status": "complete"}'))

        # Syncronization controls:
        elif cmd['command'] == 'isready':
            self.tcp.send('{"status":"readyok"}')


if __name__ == "__main__":
    # check args:
    if len(sys.argv) <= 1:
        print("Please specify --network or --manual")
        sys.exit(1)

    # set working dir:
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    # Control hal:
    f = open('config.json')
    settings = json.load(f)
    f.close()
    hal = Hal(settings)
    if sys.argv[1] == '--network':
        hal.network_control()
    elif sys.argv[1] == '--manual':
        hal.manual_control()
    elif sys.argv[1] == '--test':
        print("todo")
    else:
        print("unknown arguement")
    del(hal)
