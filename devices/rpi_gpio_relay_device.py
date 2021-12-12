#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

try:
    from utils.logger import PrintLogger
    from low_level_drivers.rpi_gpio_relay_driver import RpiGpioChannelHandler
    from nodes.message import Message
    from nodes.command import Command
    from devices.base_device import BaseDevice
except Exception:
    # here we trying to manually add our lib path to python path
    abspath = os.path.abspath("..")
    sys.path.insert(0, "{}/utils".format(abspath))
    sys.path.insert(0, "{}/low_level_drivers".format(abspath))
    sys.path.insert(0, "{}/devices".format(abspath))
    sys.path.insert(0, "{}/nodes".format(abspath))
    from command import Command
    from message import Message
    from logger import PrintLogger
    from message import Message
    from base_device import BaseDevice
    from rpi_gpio_relay_driver import RpiGpioChannelHandler


class RpiGpioRelayDevice(BaseDevice):
    """
    this wrapper cannot really check if relay open or not
    but it can save last state, selected by user
    """
    def __init__(self, name: str, pin_name: int):
        super().__init__(name)
        self._pin = pin_name
        self._relay = RpiGpioChannelHandler(pin_name)
        self._description = "this is simple test device to control one relay channel"

        on_command = Command(
            name="on",
            annotation="set relay high",
            output_kwargs={"ack_str": "ack"}
        )

        off_command = Command(
            name="off",
            annotation="set relay low",
            output_kwargs={"ack_str": "ack"}
        )

        self._available_commands.extend([on_command, off_command])
        self._state = "off"

    def device_commands_handler(self, command, **kwargs):
        if command == "on":
            self._relay.set_state(True)
            self._state = "on"
        if command == "off":
            self._relay.set_state(False)
            self._state = "off"
