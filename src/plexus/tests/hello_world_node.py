#!/usr/bin/env python3
# -*- coding: utf-8 -*-
try:
    from src.plexus.nodes import BaseNode, PeriodicCallback, Message
except Exception:
    from plexus.nodes.node import BaseNode, PeriodicCallback



class HelloWorldNode(BaseNode):
    """

    """
    def __init__(self, endpoint: str, network: list, is_daemon: bool = True):
        super().__init__(endpoint, network, is_daemon)
        self._annotation = "node for system tests"
        self.sleep_timer_delay = 0  # global sleep interval can be modified inside system_timer in ms
        self.time_quant = 10  # ms

    def custom_preparation(self):
        self.logger("custom init")
        self.system_stage_flag = "started"
        self.system_timer = PeriodicCallback(self.on_system_timer, self.time_quant)  # ms
        self.system_timer.start()


    def on_system_timer(self):
        if self.sleep_timer_delay > 0:
            # it means that we have to wait some more time
            # lets decrease global delay timer
            self.sleep_timer_delay = self.sleep_timer_delay - self.time_quant

        else:
            self.logger("test periodic callback is alive!")
            self.sleep_timer_delay = 2000  #ms


if __name__ == "__main__":
    network1 = [
        {"address": "tcp://10.9.0.24:5678"}
    ]
    n1 = HelloWorldNode(endpoint=network1[0]['address'], network=network1)
    n1.start()
    n1.join()
