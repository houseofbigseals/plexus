#!/usr/bin/env python3

import sys, os
import time
# from typing import Any
import zmq
import argparse
import uuid
# from zmq.eventloop.ioloop import IOLoop, PeriodicCallback
# from zmq.eventloop.zmqstream import ZMQStream
# import datetime

try:
    from utils.logger import PrintLogger
    from nodes.node2 import BaseNode, PeriodicCallback, Message
except ModuleNotFoundError:
    # here we trying to manually add our lib path to python path
    abspath = os.path.abspath("..")
    sys.path.insert(0, "{}/utils".format(abspath))
    sys.path.insert(0, "{}/nodes".format(abspath))
    from node2 import BaseNode, PeriodicCallback
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
        self.context = zmq.Context.instance()

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
                                                 "last_msg_received": None,
                                                 "info": None,
                                                 "last_info_received": None}

                self.logger("self network state: {}".format(self.network_state))

                # for now we will keep socket instance,  stream instance, last_time, and status
                self._sockets[n["name"]] = {"socket": new_socket,
                                            "address": n["address"],
                                            "status": "not_started"}

                self.logger(self._sockets[n["name"]])
        time.sleep(1)  # without that pause all stuff crushes



    def send_msg(self, msg_to_send: Message):
        """
        main function of all api
        send and blocking wait for response for selected timeout

        :return:
        """
        # find correct socket
        self.logger("try to send msg {} to {}".format(msg_to_send.msg_dict, msg_to_send.addr))
        sock = self._sockets[msg_to_send.addr]["socket"]
        self.logger(sock)
        msg = msg_to_send.create_zmq_msg()
        self.logger(msg)
        sd = sock.send_multipart(msg ) #, flags=zmq.NOBLOCK)
        self.logger("msg sent, lets wait for resp")
        answer = sock.recv_multipart()#flags=zmq.NOBLOCK)
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

    def get_full_node_info(self, nodename: str):
        """
        returns info about node with list of custom node commands and list of all devices and their state
        :return:
        """
        # self.logger("get_full_node_info starts")
        info_message = Message(
            addr=str(nodename),
            device=str(nodename),
            command="info",
            msg_id=uuid.uuid4().hex,
            time_=time.time()
        )
        res = self.send_msg(info_message)
        addr_decoded_, decoded_resp_ = Message.parse_zmq_msg(res)
        self.logger("we got resp from node: {}".format(nodename))
        for i in decoded_resp_:
            self.logger((i, type(i)))
        # all_answer = decoded_resp_["data"]

        self.logger("{} - {}".format("device", decoded_resp_["device"]))
        self.logger("{} - {}".format("command", decoded_resp_["command"]))
        # self.logger("get_full_node_info ends")
        return addr_decoded_, decoded_resp_

    def get_full_device_info(self, nodename, devname):
        """
        returns info about selected device with its commands and correspond params
        :return:
        """
        pass

    # ===========================================================================================================
    # user args parser and other utils to make messaging more simple

    def user_input_parse(self):
        """
        simple method to parse and complete user commands from shell
        it uses argparse to handle user input
        and own send method to communicate with other nodes
        """





if __name__ == "__main__":
    # list_of_nodes1 = [
    #     {"name": "node1", "address": "tcp://192.168.100.4:5566"},
    #     {"name": "node2", "address": "tcp://192.168.100.8:5567"},
    #     {"name": "node3", "address": "tcp://192.168.100.8:5568"}
    # ]
    list_of_nodes1 = [
        {"name": "node1", "address": "tcp://10.9.0.23:5566"}
        # {"name": "node1", "address": "tcp://10.9.0.23:5566"},
        # {"name": "node2", "address": "tcp://192.168.100.8:5567"},
        # {"name": "node3", "address": "tcp://192.168.100.8:5568"}
    ]
    user_api = PlexusUserApi(endpoint="tcp://10.9.0.21:5565", name="client", list_of_nodes=list_of_nodes1)

    user_api.get_full_node_info("node1")

    user_device = input("select device: ")


