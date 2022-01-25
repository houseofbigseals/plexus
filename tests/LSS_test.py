#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import os, sys
import time

# custom path imports
try:
    from nodes.node2 import BaseNode, PeriodicCallback, Message
    from utils.console_client_api import PlexusUserApi
    # from nodes.broker import BrokerNode
    from devices.rpi_gpio_relay_device import RpiGpioRelayDevice
    from devices.bmp180_device import BMP180Sensor
    from devices.si7021_device import SI7021
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
    from si7021_device import SI7021
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
        # self.vent_pump_3 = RpiGpioRelayDevice("vent_pump_3", 6)
        # self.vent_pump_4 = RpiGpioRelayDevice("vent_pump_4", 12)
        self.coolers_12v = RpiGpioRelayDevice("coolers_12v", 13)
        self.air_valve_2 = RpiGpioRelayDevice("air_valve_2", 19)
        self.air_valve_3 = RpiGpioRelayDevice("air_valve_3", 26)
        self.vent_pump_5 = RpiGpioRelayDevice("vent_pump_5", 16)
        self.vent_pump_6 = RpiGpioRelayDevice("vent_pump_6", 20)
        # self.ch7 = RpiGpioRelayDevice("ch7", 16)
        # self.ch8 = RpiGpioRelayDevice("ch8", 20)

        self.led = LedUartDevice(
            devname='/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0',
            name="led"
        )
        self.bmp180 = BMP180Sensor("bmp180")
        self.si7021 = SI7021("si7021")

        self._annotation = "lss node for system tests"

        self._devices.extend([
            self.n2_valve, self.vent_pump_5, self.vent_pump_6, self.coolers_12v,
            self.air_valve_2, self.air_valve_3, self.ch7, self.ch8, self.bmp180,
            self.led, self.si7021
            ])

        self.sleep_timer_delay = 0  # global sleep interval can be modified inside system_timer in ms
        self.system_stage_flag = "waiting for start"
        self.time_quant = 10  # ms
        self.current_led_mode = [40, 40]  #mA


        # whole search loop:

        # 0. getting new light mode for new measuring point
        # 1. "waiting for start"
        # 2. open air valves
        # 3. "waiting for opening air valves"
        # 4. start air pumps
        # 5. open n2 valve
        # 6. start co2-sensor calibration
        # 7. "waiting for co2 sensor calibration with n2 "
        # 8. stop co2-sensor calibration
        # 9. close n2 valve
        # 10. "waiting for before-leds delay"
        # 11. set new leds mode
        # 12. "waiting for the end of air purge"
        # 13. stop air pumps
        # 14. close air valves
        # 15. "waiting for the end of co2 measuring period"
        # 16. calculate results for just measured point - F, Q or smth else
        # 17. check calculated results, calculate next search point

    # Wait 15 seconds for them to open
    # here we want to wait a lot of time, like 15 seconds
    # but we dont want to block other async tasks in main node process
    # so we have to use some crutch:
    # we will create global timer variable and every tick of main timer we will decrease it
    #



    def custom_preparation(self):
        self.logger("custom init")

        self.system_stage_flag = "waiting for the end of co2 measuring period"


        self.system_timer = PeriodicCallback(self.on_system_timer, self.time_quant)  # ms
        self.system_timer.start()
        self.logger("shut off all relays")
        for ch in [self.n2_valve, self.vent_pump_5, self.vent_pump_6, self.coolers_12v,
                    self.air_valve_2, self.air_valve_3, self.ch7, self.ch8]:
            ch.call("on")  # because they are inverted



    def on_system_timer(self):
        # t = datetime.datetime.now().time()

        if self.sleep_timer_delay > 0:
            # it means that we have to wait some more time
            # lets decrease global delay timer
            self.sleep_timer_delay = self.sleep_timer_delay - self.time_quant

        else:
            # it means that new search stage started
            # lets check what flag is set on now
            if self.system_stage_flag == "waiting for start":
                # it means that it is time to start new step
                self.logger("it is time to start air draining cycle")
                # 1. open air valves
                self.air_valve_2.call("off")
                self.air_valve_3.call("off")
                # now we have to wait for opening them for 15 seconds
                # lets set new flag and delay value
                self.system_stage_flag = "waiting for opening air valves"
                self.sleep_timer_delay = 15000  # ms
                self.logger(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
                # then break

            elif self.system_stage_flag == "waiting for opening air valves":
                # it means that  it is time to start air draining
                # 4. start air pumps
                self.logger("it is time to start air pumps")
                self.vent_pump_5.call("off")
                self.vent_pump_6.call("off")

                # then start co2 sensor calibration
                # in LSS mode - we dont need it

                # 5. open n2 valve
                # 6. start co2-sensor calibration
                # 7. "waiting for co2 sensor calibration with n2 "
                # 8. stop co2-sensor calibration
                # 9. close n2 valve
                # 10. "waiting for before-leds delay"
                # 11. set new leds mode
                self.system_stage_flag = "waiting for the end of air purge"
                self.sleep_timer_delay = 120000  # ms - 2 mins
                self.logger(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))

            elif self.system_stage_flag == "waiting for the end of air purge":
                # it is time to close air valves and stop air pump
                self.logger("it is time to stop air purge")
                self.air_valve_2.call("on")
                self.air_valve_3.call("on")
                self.vent_pump_5.call("on")
                self.vent_pump_6.call("on")

                self.system_stage_flag = "waiting for the end of co2 measuring period"
                self.sleep_timer_delay = 120000  # ms - 2 mins
                self.logger(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))

            elif self.system_stage_flag == "waiting for the end of co2 measuring period":
                # time to configure delay for new search point
                # self.logger("it is time to set new search point")

                self.system_stage_flag = "waiting for the end of co2 measuring period"
                # self.logger(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
                # here we want to wait for new round date like 18.05 or 21.10
                # we dont want to calculate it, so we will not change flag until
                # this time have come
                tn = datetime.datetime.now()
                if tn.time().minute % 5 == 0 and tn.time().second == 0:
                    self.system_stage_flag = "waiting for start"
                    self.logger(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
                    self.logger("the time for new step has come")
                else:
                    self.sleep_timer_delay = 100


if __name__ == "__main__":
    list_of_nodes1 = [
        {"name": "node1", "address": "tcp://10.9.0.23:5566"},
    ]
    n1 = LSSNode(name=list_of_nodes1[0]['name'], endpoint=list_of_nodes1[0]['address'],
                     list_of_nodes=list_of_nodes1)
    n1.start()
    n1.join()
