
# base imports
from datetime import datetime
import os, sys
import time

# custom path imports
try:
    from nodes.node2 import BaseNode, PeriodicCallback
    from utils.console_client import PlexusUserApi
    # from nodes.broker import BrokerNode
    from devices.numlock_device import NumLockDevice
except ModuleNotFoundError:
    # here we trying to manually add our lib path to python path
    abspath = os.path.abspath("..")
    sys.path.insert(0, "{}/nodes".format(abspath))
    sys.path.insert(0, "{}/devices".format(abspath))
    sys.path.insert(0, "{}/utils".format(abspath))
    from node2 import BaseNode, PeriodicCallback
    from console_client import PlexusUserApi
    from numlock_device import NumLockDevice


# # primitive config
# # test1
# test1_addr = "tcp://192.168.100.4:5566"
# test1_name = "test1"
#
# # test2
# endpoint2_addr = "tcp://192.168.100.8:5566"
# endpoint2_name = "test2"


class TestLedNode(BaseNode):
    """

    """
    def __init__(self, endpoint: str, name: str, list_of_nodes: list, is_daemon: bool = True):
        super().__init__(endpoint, name, list_of_nodes, is_daemon)
        self._led_device = NumLockDevice(name="numlock")
        self._devices.append(self._led_device)
        self.led_period = 5000


    def custom_preparation(self):
        # here user must do all preparations
        # also create and start all PeriodicCallback tasks
        # like that:
        # self.check_timer = PeriodicCallback(self.on_timer, self.period)
        # self.check_timer.start()
        self.led_timer = PeriodicCallback(self.on_led_timer, self.led_period)
        self.led_timer.start()

    def on_led_timer(self):

        res = self._led_device.call("get_state")
        print("led device current state: {}".format(res))
        if str(res) == "on":
            self._led_device.call("set_state", **{"new_state": 0})
            print("new led device current state: {}".format(self._led_device.call("get_state")))
        if str(res) == "off":
            self._led_device.call("set_state", **{"new_state": 1})
            print("new led device current state: {}".format(self._led_device.call("get_state")))


    def custom_request_parser(self, stream, from_addr: str, msg_dict: dict):
        # here user can add custom parsing of received message
        # if msg_dict["command"] ==
        pass

    def custom_response_parser(self, stream,  from_addr: str, msg_dict: dict, reqv_msg):
        # here user can add custom parsing of received answer for his message
        pass


if __name__ == '__main__':
    list_of_nodes1 = [
        {"name": "node1", "address": "tcp://192.168.100.4:5566"},
        {"name": "node2", "address": "tcp://192.168.100.8:5567"},
        {"name": "node3", "address": "tcp://192.168.100.8:5568"}
    ]
    n1 = TestLedNode(name=list_of_nodes1[0]['name'], endpoint=list_of_nodes1[0]['address'],
                     list_of_nodes=list_of_nodes1)
    # n2 = TestLedNode(name="node2", endpoint="tcp://192.168.100.4:5567", list_of_nodes=list_of_nodes1)
    # n3 = TestLedNode(name="node3", endpoint="tcp://192.168.100.4:5568", list_of_nodes=list_of_nodes1)
    n1.start()
    client = PlexusUserApi(endpoint="tcp://192.168.100.4:5565", name="client", list_of_nodes=list_of_nodes1)
    client.start()
    # n2.start()
    time.sleep(5.2)
    print("client.get_all_nodes_info() : {}".format(client.get_all_nodes_info()))
    time.sleep(5.2)
    print("client.get_all_nodes_info() : {}".format(client.get_all_nodes_info()))
    # n3.start()
    # n2.join()
    n1.join()

