
# base imports
from datetime import datetime
import os, sys
import time

# custom path imports
try:
    from nodes.node import UserNode, PeriodicCallback
    from nodes.broker import BrokerNode
    from devices.numlock_device import NumLockDevice
except ModuleNotFoundError:
    # here we trying to manually add our lib path to python path
    abspath = os.path.abspath("..")
    sys.path.insert(0, "{}/nodes".format(abspath))
    from node import UserNode, PeriodicCallback
    from broker import BrokerNode
    sys.path.insert(0, "{}/devices".format(abspath))
    from numlock_device import NumLockDevice


# primitive config
# test1
test1_addr = "tcp://192.168.100.4:5566"
test1_name = "test1"

# test2
endpoint2_addr = "tcp://192.168.100.8:5566"
endpoint2_name = "test2"


class TestLedNode(UserNode):
    """

    """
    def __init__(self):
        super().__init__(endpoint=test1_addr, name=test1_name, is_daemon=True)
        self._led_device = NumLockDevice(name="numlock")
        self._devices.append(self._led_device)




    # ========= abstract methods, those must be redefined by user ==========
    def user_run(self):
        # here user must do all preparations
        # also create and start all PeriodicCallback tasks
        # like that:
        # self.check_timer = PeriodicCallback(self.on_timer, self.period)
        # self.check_timer.start()
        pass

    def user_request_parser(self, from_addr, command, msg_dict):
        # here user can add custom parsing of received message
        if command == "blink":



    def user_response_parser(self, from_addr, command, msg_dict):
        # here user can add custom parsing of received answer for his message
        pass

