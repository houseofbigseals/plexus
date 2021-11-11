import random
import time
import zmq

from zmq.eventloop.ioloop import IOLoop, PeriodicCallback
from zmq.eventloop.zmqstream import ZMQStream
from multiprocessing import Process
from datetime import datetime
import os, sys, pickle

try:
    from utils.config_parser import ConfigParser
    from utils.logger import PrintLogger
except ModuleNotFoundError:
    # here we trying to manually add our lib path to python path
    abspath = os.path.abspath("..")
    sys.path.insert(0, "{}/utils".format(abspath))
    from config_parser import ConfigParser
    sys.path.insert(0, "{}/utils".format(abspath))
    from logger import PrintLogger


class BrokerNode(Process):
    """

    """
    def __init__(self, name: str, endpoint: str, is_daemon: bool = True, dict_of_brokers: dict = None):
        Process.__init__(self, daemon=is_daemon)
        # lets parse config
        self.name = name
        self.logger = PrintLogger(self.name)
        self.logger(" start init")

        self.front_endpoint = endpoint
        dict_of_brokers.pop(self.name)  # remove itself
        self.dict_of_brokers = dict_of_brokers

        # mb in future there will be nodes from config
        # but for now we will add only encoded node names, who have sent any msg to that broker
        self.nodes = {}
        # Prepare our context and sockets
        self.context = zmq.Context()
        self.reqv_socket = None
        # self.resp_socket = None
        # self.ping_timer_interval = 1000
        self.ping_brokers_timer = None
        self.main_stream = None
        self.logger(" end init")


    def run(self):
        """
        this method will be called when the broker start() function is called by user
        :return:
        """
        self.logger(" start run")
        self.reqv_socket = self.context.socket(zmq.ROUTER)
        self.reqv_socket.identity = (u"{}".format(self.name)).encode('ascii')
        self.reqv_socket.bind(self.front_endpoint)
        self.main_stream = ZMQStream(self.reqv_socket)
        self.main_stream.on_recv(self.reqv_callback)
        # self.main_stream.on_send(self.resp_callback)
        # ===============================================
        self.broker_ping_socket = self.context.socket(zmq.ROUTER)
        self.broker_ping_socket.identity = (u"{}".format(self.name)).encode('ascii')
        for br in self.dict_of_brokers:
            self.broker_ping_socket.connect(self.dict_of_brokers[br])
        self.ping_stream = ZMQStream(self.broker_ping_socket)
        self.ping_stream.on_recv(self.reqv_callback)

        # ==============================================

        # start timer
        self.ping_brokers_timer = PeriodicCallback(self.ping_brokers, 1000)
        # self.check_timer2 = PeriodicCallback(self.on_timer2, 5000)
        self.ping_brokers_timer.start()
        # self.check_timer2.start()

        self.loop = IOLoop.current()  # do we need it ?
        self.logger(" go to loop")
        self.loop.start()

    def reqv_callback(self, msg):
        self.logger(" got msg {}".format(msg))
        from_addr = msg[0]  # was added automatically
        # lets check if this addr in our nodes dict
        if from_addr not in self.nodes.keys():
            self.nodes.update({from_addr: datetime.now()})

        to_addr = msg[2]
        msg_body = msg[4]
        msg_dict = pickle.loads(msg_body)
        # there is a list of system commands that we use under the hood
        # 2) check if it is command to broker itself
        if msg_dict["device"] == self.name:
            # it means that msg was sent directly to broker
            if msg_dict["command"] == "PING":
                self.logger(" got PING from {}".format(from_addr))
                # TODO update container with nodes with this node and this time
                new_msg_dict = {
                    "id": msg_dict["id"],
                    "command": "RESP",
                    "device": from_addr,
                    "data": msg_dict["data"],
                    "time": datetime.now()
                }

                # self.handle_system_msgs(from_addr, msg_dict)
                msg_to_send = [from_addr, b'', self.name.encode('ascii'), b'', pickle.dumps(new_msg_dict)]
                self.main_stream.send_multipart(msg_to_send)

        else:
            # simply resend this msg to its goal node
            msg_to_send = [to_addr, b'', from_addr, b'', msg_body]
            self.logger(" send msg {}".format(msg_to_send))
            self.main_stream.send_multipart(msg_to_send)

    def ping_brokers(self):
        """Method called on timer expiry.
        :rtype: None
        """
        self.logger(" fast async timer works again! - {}".format(datetime.now()))

        for b in self.dict_of_brokers:
            self.logger(" send broker ping to - {}".format(b))
            msg_to_send = [b.encode('ascii'), b'', self.name.encode('ascii'), b'', b'PING']
            self.ping_stream.send_multipart(msg_to_send)

        # self.logger(" saved addrs:")
        # for i in self.nodes:
        #     print("{}: {}".format(i, self.nodes[i]))


if __name__ == "__main__":
    # example:

    # exp_config = {
    #     "experiment": "test1",
    #     "description": "nice test experiment",
    #     "brokers":
    #     {
    #         "pc1": {
    #             "addr": "tcp://192.168.100.4:5566", "nodes":
    #             {
    #                 "node1": {"description": "temp", "devices": {}},
    #                 "node2": {"description": "temp", "devices": {}},
    #                 "node3": {"description": "temp", "devices": {}},
    #              },
    #         },
    #         "pc2": {
    #             "addr": "tcp://192.168.100.8:5566", "nodes":
    #             {
    #                 "node6": {"description": "temp", "devices": {}},
    #                 "node4": {"description": "temp", "devices": {}},
    #                 "node5": {"description": "temp", "devices": {}},
    #             },
    #         }
    #     }
    # }
    # c = ConfigParser()
    # c.init_from_dict(exp_config)
    # c.show_pretty_graph()
    brokers = {"pc2": "tcp://192.168.100.4:5567", "pc1": "tcp://192.168.100.4:5566", "pc3": "tcp://192.168.100.4:5568"}
    broker1 = BrokerNode(name="pc1", endpoint="tcp://192.168.100.4:5566", is_daemon=True, dict_of_brokers=brokers)
    broker2 = BrokerNode(name="pc2", endpoint="tcp://192.168.100.4:5567", is_daemon=True, dict_of_brokers=brokers)
    broker1.start()
    broker2.start()
    broker1.join()
