#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from plexus.nodes.node import BaseNode, PeriodicCallback, Message
from plexus.devices.simple_avr_relay_device import AVRRelayDevice


class StandControlNode(BaseNode):
    """

    """
    def __init__(self, endpoint: str, network: list):
        super().__init__(endpoint, network)

        self.avr_relay_dev = AVRRelayDevice(
            name="avr_relay",
            num_of_channels=6,
            dev='/dev/ttyUSB0',
            baud=9600,
            timeout=1,
            slave_id=1
        )

        self._annotation = "control node for relay control"
        self.add_device(self.avr_relay_dev)
        self.logger("my system commands")
        self.logger(self.system_commands)

    def custom_preparation(self):
        pass


if __name__ == "__main__":

    print("we are awaiting tcp addr in format 10.9.0.1")
    # we are awaiting addr as 10.9.0.1
    my_addr = str(sys.argv[1])
    print(type(my_addr))

    network1 = [
        {"address": "tcp://{}:5569".format(my_addr)}
    ]
    n1 = StandControlNode(endpoint=network1[0]['address'], network=network1)
    n1.start()
    n1.join()

