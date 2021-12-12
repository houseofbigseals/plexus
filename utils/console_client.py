#!/usr/bin/env python3

import argparse, sys, os
import time
from typing import Any
import zmq
from zmq.eventloop.ioloop import IOLoop, PeriodicCallback
from zmq.eventloop.zmqstream import ZMQStream
import datetime

try:
    from utils.logger import PrintLogger
    from nodes.node2 import BaseNode, PeriodicCallback, Message
except ModuleNotFoundError:
    # here we trying to manually add our lib path to python path
    abspath = os.path.abspath("..")
    sys.path.insert(0, "{}/utils".format(abspath))
    sys.path.insert(0, "{}/nodes".format(abspath))
    from node2 import BaseNode, PeriodicCallback, uuid
    from message import Message
    from logger import PrintLogger


class PlexusUserApi:
    """
    all methods to remotely use and control desired group of nodes
    you have manually add correct exp network config
    and also manually add security sertificates

    """

    def __init__(self, endpoint: str, name: str, list_of_nodes: list):
        # super(PlexusUserApi, self).__init__(name=name, endpoint=endpoint, list_of_nodes=list_of_nodes)
        # base node preparations like creating sockets
        # preparations that user dont want to see
        self.name = name
        self.logger = PrintLogger(name)
        self.logger("start init")

        self._endpoint = endpoint
        self.loop = None
        self.list_of_nodes = list_of_nodes
        self.network_state = dict()
        # Prepare our context and sockets
        self.context = zmq.Context()

        # lets create your main socket with bind option
        self._socket = self.context.socket(zmq.ROUTER)
        self._socket.identity = "{}".format(self.name).encode('ascii')
        self.logger("{}".format(self.name).encode('ascii'))
        self._socket.bind(self._endpoint)
        # self.main_stream = ZMQStream(self._socket)
        # self.main_stream.on_recv_stream(self.reqv_callback)
        self.network_state = dict()
        self._sockets = dict()

        # then lets create lots of sockets for all other nodes from given list
        for n in self.list_of_nodes:
            if n["name"] != self.name:
                # create router socket and append it to self._sockets
                new_socket = self.context.socket(zmq.ROUTER)
                new_socket.identity = "{}".format(self.name).encode('ascii')
                self.logger("{}".format(n["name"]).encode('ascii'))
                new_socket.connect(n["address"])

                # new_stream = ZMQStream(new_socket)
                # new_stream.on_recv_stream(self.reqv_callback)

                # lets create big dict for every node in list, with
                self.network_state[n["name"]] = {"address": n["address"],
                                                 "status": "unknown",
                                                 "last_msg_sent": None,
                                                 "last_msg_received": None}
                self.logger("self network state: {}".format(self.network_state))

                # for now we will keep socket instance,  stream instance, last_time, and status
                self._sockets[n["name"]] = {"socket": new_socket,
                                            "address": n["address"],
                                            "status": "not_started"}

                self.logger(self._sockets[n["name"]])

        # self.ping_timer = PeriodicCallback(self.on_ping_timer, self.ping_period)


    def send_msg(self, msg_to_send: Message):
        """
        main function of all api
        send and blocking wait for response for selected timeout

        :return:
        """
        # find correct socket
        self.logger("try to send msg {} to {}".format(msg_to_send.msg_dict, msg_to_send.addr))
        sock = self._sockets[msg_to_send.addr]["socket"]
        msg = msg_to_send.create_zmq_msg()
        sock.send_multipart(msg)
        answer = sock.recv_multipart()
        # self.logger(answer)
        return answer


    # =================================================================================================
    # messaging primitive wrappers

    def get_all_nodes_info(self):
        """
        returns list of all nodes from config with their addr and state
        :return:
        """
        self.logger("self network state: {}".format(self.network_state))
        return self.network_state

    def get_full_node_info(self, nodename):
        """
        returns info about node with list of custom node commands and list of all devices and their state
        :return:
        """
        pass

    def get_full_device_info(self):
        """
        returns info about selected device with its commands and correspond params
        :return:
        """
        pass



    # ===========================================================================================================
    # user args parser and other utils to make messaging more simple

    def args_parse(self):
        pass


def parse():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()


if __name__ == "__main__":
    list_of_nodes1 = [
        {"name": "node1", "address": "tcp://192.168.100.4:5566"},
        {"name": "node2", "address": "tcp://192.168.100.8:5567"},
        {"name": "node3", "address": "tcp://192.168.100.8:5568"}
    ]
    user_api = PlexusUserApi(endpoint="tcp://192.168.100.4:5565", name="client1", list_of_nodes=list_of_nodes1)


