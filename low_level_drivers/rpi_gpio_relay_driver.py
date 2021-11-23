#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RPI gpio relay handler, for working withh relay directly
you have to connect relay module such as in that video
https://medium.com/@jinky32/connecting-a-12v-8-channel-relay-to-an-external-power-supply-and-raspberrypi-6fec119c112c
because we are using 12dc external pover supply
do not connect rpi GND with relay GND !
default pinout:
RELAY JD_VCC -> external 12VDC+
RELAY GND -> external 12VDC-
RELAY VCC -> RPI 3.3V
RELAY CH1 -> RPI GPIO5
RELAY CH2 -> RPI GPIO6
RELAY CH3 -> RPI GPIO12
RELAY CH4 -> RPI GPIO13
RELAY CH5 -> RPI GPIO19
RELAY CH6 -> RPI GPIO26
RELAY CH7 -> RPI GPIO16
RELAY CH8 -> RPI GPIO20
it works somehow and i dont know how exactly
"""


# from copy import deepcopy
# import time
# from collections import OrderedDict, namedtuple

try:
    # import gpiozero
    from gpiozero import LED
except Exception as e:
    print(e)


class RpiGpioChannelHandler:
    """

    """
    def __init__(self, pin_name: int):
        self.pin = pin_name
        self.channel = LED(self.pin)

    def set_state(self, state: bool):
        if state:
            self.channel.on()
        else:
            self.channel.off()
