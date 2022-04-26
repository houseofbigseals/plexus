#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime


try:
    from src.plexus.nodes import BaseNode, PeriodicCallback, Message
    from src.plexus.utils.console_client_api import PlexusUserApi
    # from nodes.broker import BrokerNode
    # from src.plexus.devices.rpi_gpio_relay_device import RpiGpioRelayDevice
    # from src.plexus.devices.bmp180_device import BMP180Sensor
    # from src.plexus.devices import SI7021
    # from src.plexus.devices.led_uart_device import LedUartDevice
except Exception:

    from plexus.nodes.node import BaseNode, PeriodicCallback
    from plexus.nodes.message import Message
    from plexus.nodes.command import Command
    from plexus.utils.console_client import PlexusUserApi


class SimpleNode(BaseNode):
    """

    """
    def __init__(self, endpoint: str, list_of_nodes: list, is_daemon: bool = True):
        super().__init__(endpoint, list_of_nodes, is_daemon)

    def custom_preparation(self):
        self.logger("custom init")
        self.system_timer = PeriodicCallback(self.on_system_timer, 3000)  # ms
        self.system_timer.start()

    def on_system_timer(self):
        self.logger("hey!")
        self.logger("self network state: {}".format(self.network_state))


if __name__ == "__main__":
    list_of_nodes1 = [
        "tcp://10.9.0.23:5566"
    ]
    n1 = SimpleNode(endpoint="tcp://10.9.0.21:5555", list_of_nodes=list_of_nodes1)
    n1.start()
    n1.join()

