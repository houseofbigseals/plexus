#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import os, sys

# custom path imports
try:
    from nodes.node2 import BaseNode, PeriodicCallback, Message
    from utils.console_client_api import PlexusUserApi
    # from nodes.broker import BrokerNode
    from devices.rpi_gpio_relay_device import RpiGpioRelayDevice
    from devices.bmp180_device import BMP180Sensor
    from devices.led_uart_device import LedUartDevice
except Exception:
    # here we trying to manually add our lib path to python path
    abspath = os.path.abspath("..")
    print(abspath)
    sys.path.insert(0, "{}/nodes".format(abspath))
    sys.path.insert(0, "{}/devices".format(abspath))
    sys.path.insert(0, "{}/utils".format(abspath))
    print(sys.path)
    from node2 import BaseNode, PeriodicCallback
    from message import Message
    from console_client import PlexusUserApi
    from rpi_gpio_relay_device import RpiGpioRelayDevice
    from bmp180_device import BMP180Sensor
    from led_uart_device import LedUartDevice



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


class LSSNode(BaseNode):
    """

    """
    def __init__(self, endpoint: str, name: str, list_of_nodes: list, is_daemon: bool = True):
        super().__init__(endpoint, name, list_of_nodes, is_daemon)
        # init relays
        self.n2_valve = RpiGpioRelayDevice("n2_valve", 5)
        self.vent_pump_3 = RpiGpioRelayDevice("vent_pump_3", 6)
        self.vent_pump_4 = RpiGpioRelayDevice("vent_pump_4", 12)
        self.coolers_12v = RpiGpioRelayDevice("coolers_12v", 13)
        self.air_valve_2 = RpiGpioRelayDevice("air_valve_2", 19)
        self.air_valve_3 = RpiGpioRelayDevice("air_valve_3", 26)
        self.ch7 = RpiGpioRelayDevice("ch7", 16)
        self.ch8 = RpiGpioRelayDevice("ch8", 20)

        self.led = LedUartDevice(
            devname='/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0',
            name="led"
        )
        self.bmp180 = BMP180Sensor("bmp180")

        self._annotation = "lss node for system tests"

        self._devices.extend([
            self.n2_valve, self.vent_pump_3, self.vent_pump_4, self.coolers_12v,
            self.air_valve_2, self.air_valve_3, self.ch7, self.ch8, self.bmp180,
            self.led
            ])


    def custom_preparation(self):
        # here user must do all preparations
        # also create and start all PeriodicCallback tasks
        # like that:
        # self.check_timer = PeriodicCallback(self.on_timer, self.period)
        # self.check_timer.start()
        self.logger("custom init")
        self.system_timer = PeriodicCallback(self.on_system_timer, 1000)
        self.system_timer.start()
        self.logger("shut off all relays")
        for ch in self._devices:
            ch.call("on")  # because they are inverted

    def on_system_timer(self):
        t = datetime.datetime.now().time()
        if t.minute % 15 == 0 and t.second == 0:
            self.logger("it is time to start air draining cycle")
            # 1. open air valves
            # 2. wait 15 seconds for them to open
            # 3. start air drain pumps
            # 4. wait t1 interval
            # 5. start co2 sensor calibration
            # 6.
