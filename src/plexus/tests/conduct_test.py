#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import serial

# custom path imports
try:
    from plexus.nodes.node import BaseNode, PeriodicCallback
    from plexus.nodes.message import Message
    from plexus.utils.console_client import PlexusUserApi
    from plexus.devices.simple_avr_relay_device import AVRRelayDevice
    from plexus.devices.simple_avr_cond_device import AVRCondDevice
except Exception as e:
    from src.plexus.nodes.node import BaseNode, PeriodicCallback, Message
    from src.plexus.utils.console_client_api import PlexusUserApi
    from src.plexus.devices.simple_avr_relay_device import AVRRelayDevice
    from src.plexus.devices.simple_avr_cond_device import AVRCondDevice
#     # from nodes.broker import BrokerNode
#     from src.plexus.devices.rpi_gpio_relay_device import RpiGpioRelayDevice
#     from src.plexus.devices.bmp180_device import BMP180Sensor
#     from src.plexus.devices import SI7021
#     from src.plexus.devices.led_uart_device import LedUartDevice
#     from src.plexus.devices.sba5_device import SBA5Device
#     from src.plexus.devices.simple_avr_relay_device import SimpleRelayControl

# except Exception as e:

    # from plexus.devices.rpi_gpio_relay_device import RpiGpioRelayDevice
    # from plexus.devices.bmp180_device import BMP180Sensor
    # from plexus.devices.si7021_device import SI7021
    # from plexus.devices.led_uart_device import LedUartDevice
    # from plexus.devices.sba5_device import SBA5Device



class ConductStandControlNode(BaseNode):
    """

    """
    def __init__(self, endpoint: str, name: str, list_of_nodes: list, is_daemon: bool = True):
        super().__init__(endpoint, name, list_of_nodes, is_daemon)
        self.avr_relay_dev = AVRRelayDevice(
            name="avr_relay",
            num_of_channels=6,
            dev='/dev/ttyUSB0',
            baud=9600,
            timeout=1,
            slave_id=1
        )

        self.avr_cond_dev = AVRCondDevice(
            name="avr_sensor",
            dev='/dev/ttyUSB1',
            baud=9600,
            timeout=1,
            slave_id=2
        )

        self._annotation = "control node for conductivity control stand with mixer"
        self._devices.extend([self.avr_cond_dev, self.avr_relay_dev])

    def custom_preparation(self):
        self.logger("custom init")



if __name__ == "__main__":
    list_of_nodes1 = [
        {"name": "node2", "address": "tcp://10.9.0.1:5567"}
        # {"name": "node2", "address": "tcp://10.9.0.12:5567"},
    ]
    n1 = ConductStandControlNode(name=list_of_nodes1[0]['name'], endpoint=list_of_nodes1[0]['address'],
                     list_of_nodes=list_of_nodes1)
    n1.start()
    n1.join()

