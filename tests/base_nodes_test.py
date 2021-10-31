import os
import sys
from time import sleep
# from random import uniform
from zmq.eventloop.ioloop import IOLoop, PeriodicCallback
import random, uuid

try:
    from low_level_drivers.virtual_device_driver import VirtualDeviceHandler
    from nodes.node import UserNode
except ModuleNotFoundError:
    # here we trying to manually add our lib path to python path
    abspath = os.path.abspath("..")
    # print(abspath)
    sys.path.insert(0, "{}/low_level_drivers".format(abspath))
    sys.path.insert(0, "{}/nodes".format(abspath))
    # print(sys.path)

    from virtual_device_driver import VirtualDeviceHandler
    from node import UserNode
    from broker import BrokerNode


# # lets create custom node, based on base node class
class CustomNode(UserNode):
    def __init__(self, front_endpoint, name, is_daemon):
        super().__init__(front_endpoint, name, is_daemon)

    # how we can add functionality to custom node?
    # at first we have to create custom child class based on base node abstract class
    # it can do some technical work that we dont want to do manually, such as:
    # - periodical ping of broker and remembering last answered ping
    # - parsing base commands such as: kill, stop, start
    # - handling router socket with tornado IOLoop
    # -

    def on_timer(self):
        self.logger(" on timer called, so i will send msg")

        to_addr = u"{}".format(random.randint(1, 4)).encode('ascii')
        msg_body = "INFO from {} to {}: you are gay".format(self.name, to_addr).encode('ascii')
        self.send(to_addr, command="INFO", msg_id=uuid.uuid1(), data = msg_body)

    def user_run(self):
        self.check_timer = PeriodicCallback(self.on_timer, 1000)
        self.check_timer.start()


    def user_request_parser(self, from_addr, command, msg_dict):
        # here user can add custom parsing of received message
        pass

    def user_response_parser(self, from_addr, command, msg_dict):
        # here user can add custom parsing of received answer for his message
        pass

if __name__ == "__main__":
    broker = BrokerNode("tcp://192.168.100.4:5566", True)
    c1 = CustomNode("tcp://192.168.100.4:5566","1", True)
    c2 = CustomNode("tcp://192.168.100.4:5566", "2", True)
    c3 = CustomNode("tcp://192.168.100.4:5566", "3", True)
    c4 = CustomNode("tcp://192.168.100.4:5566", "4", True)

    broker.start()
    c1.start()
    c2.start()
    c3.start()
    c4.start()
    broker.join()

