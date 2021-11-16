import datetime
import random
import time
import uuid
import os
import sys

import zmq
import pickle

from zmq.eventloop.ioloop import IOLoop, PeriodicCallback
from zmq.eventloop.zmqstream import ZMQStream
from multiprocessing import Process
from abc import ABC, abstractmethod, abstractproperty
from typing import Any

# from broker import BrokerNode

try:
    from utils.logger import PrintLogger
except ModuleNotFoundError:
    # here we trying to manually add our lib path to python path
    abspath = os.path.abspath("..")
    # print(abspath)
    # sys.path.insert(0, "{}/low_level_drivers".format(abspath))
    sys.path.insert(0, "{}/utils".format(abspath))

    # print(sys.path)

    from logger import PrintLogger


# commands like "kill", "stop", "status"
# must be handled by parent class in parse_msg method
# because they are very familiar for all types of nodes
# if user want to parse they manually, he must override parent methods like:
# on_kill(), on_start(), on_stop(), on_status()


# all this text descriptions are for remote user`s SCADA client
# he cannot directly call relay device, so he need some hot-plug description of
# its methods and goals

# if we need to do something else in node, except just answering to requests
# we need to create a zmq timer object in node
# and put all periodical work to different timers
# do we need to use locks and other stuff with them, or they work in one process? we need to check


class BaseNode(ABC, Process):
    """

    """

    # ========= abstract methods, those must be redefined by user ==========
    @abstractmethod
    def custom_preparation(self):
        # here user must do all preparations
        # also create and start all PeriodicCallback tasks
        # like that:
        # self.check_timer = PeriodicCallback(self.on_timer, self.period)
        # self.check_timer.start()
        pass

    @abstractmethod
    def custom_request_parser(self, stream, from_addr: str, msg_dict: dict):
        # here user can add custom parsing of received message
        pass

    @abstractmethod
    def custom_response_parser(self, stream,  from_addr: str, msg_dict: dict, reqv_msg: Any):
        # here user can add custom parsing of received answer for his message
        pass

    # ===============================================================================


    def __init__(self, endpoint: str, name: str, list_of_nodes: list, is_daemon: bool = True):
        """
        :param list_of_nodes: must be list with dicts like
        [
        {"name": "node1", "address": "tcp://192.168.100.4:5566"},
        ...
        {"name": "node100", "address": "tcp://192.168.100.4:5567"}
        ]
        :param endpoint:
        :param name:
        :param is_daemon:
        """
        Process.__init__(self, daemon=is_daemon)
        self.name = name
        self.logger = PrintLogger(self.name)
        self.logger("start init")
        self._endpoint = endpoint
        # container to keep all local devices in one place
        self._devices = []
        self.loop = None
        self.list_of_nodes = list_of_nodes
        self.network_state = dict()


        # Prepare our context and sockets
        self.context = zmq.Context()
        self._socket = None
        self.main_stream = None
        self.ping_timer = None
        self.logger("end init")
        self.status = "not_started"
        self.ping_period = 1000
        self._sockets = list()
        self._description = "abstract base node"

    # ========= tech methods, those must not be redefined by user ==========

    def run(self):
        """this method calls when user do node.start()"""
        # base node preparations like creating sockets
        # preparations that user dont want to see
        self.logger("start run")
        # lets create your main socket with bind option
        self._socket = self.context.socket(zmq.ROUTER)
        self._socket.identity = "{}".format(self.name).encode('ascii')
        self.logger("{}".format(self.name).encode('ascii'))
        self._socket.bind(self._endpoint)
        self.main_stream = ZMQStream(self._socket)
        self.main_stream.on_recv_stream(self.reqv_callback)
        self.network_state = dict()

        # then lets create lots of sockets for all other nodes from given list
        for n in self.list_of_nodes:
            if n["name"] != self.name:
                # create router socket and append it to self._sockets
                new_socket = self.context.socket(zmq.ROUTER)
                new_socket.identity = "{}".format(self.name).encode('ascii')
                self.logger("{}".format(n["name"]).encode('ascii'))
                new_socket.connect(n["address"])
                new_stream = ZMQStream(new_socket)
                new_stream.on_recv_stream(self.reqv_callback)
                # lets create big dict for every node in list, with
                self.network_state[n["name"]] = {"address": n["address"],
                                                 "status": "unknown",
                                                 "last_msg_sent": None,
                                                 "last_msg_received": None}
                self.logger("self network state: {}".format(self.network_state))

                # for now we will keep socket instance,  stream instance, last_time, and status
                self._sockets.append([n["name"], new_socket, new_stream, n["address"],
                                      datetime.datetime.now(), "not_started"])
                self.logger([n["name"], new_socket, new_stream, n["address"],
                              datetime.datetime.now(), "not_started"])

        self.ping_timer = PeriodicCallback(self.on_ping_timer, self.ping_period)

        # preparations by user like creating PeriodicalCallbacks
        self.custom_preparation()

        # the loop
        self.loop = IOLoop.current()
        self.logger("go to loop")
        self.ping_timer.start()
        self.status = "work"
        # go to endless loop with reading messages and checking PeriodicalCallbacks, created by user
        self.loop.start()

    def send(self, stream: ZMQStream, addr: str, device: str, command: str, msg_id: uuid, data: Any):
        """handler for sending data to another node through local broker """
        # prepare msg
        msg_dict = dict()
        msg_dict["device"] = device
        msg_dict["command"] = command
        msg_dict["id"] = msg_id
        msg_dict["time"] = time.time()
        msg_dict["data"] = data
        msg_encoded = pickle.dumps(msg_dict)
        # msg = [self._broker.encode('ascii'), b'', addr.encode('ascii'), b'', msg_encoded]
        # msg = [addr.encode('ascii'), b'', msg_encoded]
        msg = [addr.encode('ascii'), b'', msg_encoded]
        msg_raw = [addr, b'', msg_dict]  # for store needs
        # then put its id to queue
        self.store_awaiting_msg(msg_raw)

        # also lets save last sent msg time in network config
        self.network_state[addr]["last_msg_sent"] = time.time()
        self.logger("self network state: {}".format(self.network_state))

        self.logger("msg to {} is {}".format(addr, msg))
        # send msg
        stream.send_multipart(msg)

    def reqv_callback(self, stream, msg):
        """base callback for all messages in all streams"""
        self.logger("reqv callback")
        self.logger("we got msg: {}".format(msg))
        # parse
        # broker = msg[0]
        # empty = msg[1]
        from_addr = msg[0]
        empty = msg[1]
        msg_body = msg[2]
        msg_dict = pickle.loads(msg_body)
        self.logger(msg_dict)

        msg_id = msg_dict["id"]
        command = msg_dict["command"]
        device_name = msg_dict["device"]  # that is a str with device name
        msg_data = msg_dict["data"]
        msg_time = msg_dict["time"]

        # lets check if that node in our noeds list:
        if from_addr.decode('ascii') in self.network_state.keys():
            self.network_state[from_addr.decode('ascii')]["last_msg_received"] = time.time()
            self.logger("self network state: {}".format(self.network_state))
        else:
            self.logger("found new node by irs reqv: {}".format(from_addr.decode('ascii')))
            self.logger("we will add it to our network state container")
            # TODO mb it is good to add unknown node to our ping list?
            self.network_state[from_addr.decode('ascii')] = {"address": "unknown",  # todo how to find addr?
                                                               "status": "unknown",
                                                               "last_msg_sent": None,
                                                               "last_msg_received": time.time()}

            self.logger("self network state: {}".format(self.network_state))

        # 1) lets check if it is response for one of our requests to another node
        self.logger(msg_dict["command"])

        if command == "RESP":
            # so we dont care about "device" field
            # it means that it it resp to us and we must not answer
            answered_resp = self.extract_awaiting_msg(msg_id)
            self.logger("command RESP received in msg with id {}".format(msg_id))
            self.logger("msg body is {}".format(msg_dict))
            # here app must find original msg by its id and delete it from unanswered queue
            # also if it was resp for some system call, it must be handled here, before user parsing
            self.system_resp_handler(stream, from_addr, msg_dict, answered_resp)
            # and there - user parsing
            self.custom_response_parser(stream, from_addr, msg_dict, answered_resp)

        # there is a list of system commands that we use under the hood
        # 2) check if it is command to node
        elif device_name == self.name or device_name.decode('ascii') == self.name:
            # it means that msg was sent directly to node
            self.handle_system_msgs(stream, from_addr.decode('ascii'), msg_dict)

        # 3) check if it is command to one of our devices
        # let's check which device the message was sent to
        else:
            for device_ in self._devices:
                if device_.name == device_name:
                    # then call selected method on this device with that params
                    try:
                        result = device_.call(command, **msg_data)
                        encoded_result = pickle.dumps(result)
                        self.send(stream, from_addr, device_name, "RESP", msg_id, encoded_result)
                    except Exception as e:
                        error_str = "error while calling device: {}".format(e)
                        self.logger(error_str)
                        self.send(stream, from_addr, device_name, "RESP", msg_id, pickle.dumps(error_str))

            # this is shit and we dont want to handle it
            self.logger("command {} is not system, trying to use user handler".format(command))
            # 5) may be user want to handle it somehow
            self.custom_request_parser(stream, from_addr, msg_dict)

    def handle_system_msgs(self, stream, from_addr, msg_dict):
        """handler to base commands, those can be sent to every node by another node"""
        if msg_dict["command"] == "INFO":
            # it means that it it reqv to us and we must answer
            # in answer we need to send all info about node and its devices
            self.logger("command INFO received")
            info = {
                "name": self.name,
                "status": self.status,
                "devices": self._devices
            }
            to_addr = from_addr
            self.send(stream=stream,
                addr=to_addr,
                device=self.name,
                command="RESP",
                msg_id=msg_dict["id"],
                data=info)

        if msg_dict["command"] == "PING":
            # it means that it it reqv to us and we must answer
            # in answer we need to send all info about node and its devices
            self.logger("command PING received")
            to_addr = from_addr
            self.send(stream=stream,
                addr=to_addr,
                device=self.name,
                command="RESP",
                msg_id=msg_dict["id"],
                data="ACK".encode())

            # we have to send resp with standard info about this node and its devices

    def on_ping_timer(self):
        # method to ping other sockets
        self.logger("try to send ping")
        for s in self._sockets:
            # self._sockets.append([n["name"], new_socket, new_stream, n["address"],
            #                       datetime.datetime.now(), "not_started"])
            self.send(stream=s[2], addr=s[0], device=s[0],
                      command="PING", msg_id=uuid.uuid1(), data=b'')
            # self.network_state[s[0]]["last_ping_sent"] = time.time()

    def store_awaiting_msg(self, msg_raw: Any):
        """ user can override this method if needs"""
        # TODO

    def extract_awaiting_msg(self, msg_id: Any):
        """ user can override this method if needs"""
        # TODO
        msg = None
        return msg

    def system_resp_handler(self, stream: ZMQStream, from_addr: str, msg_dict: dict, reqv_msg: Any):
        """ user can override this method if needs"""
        # TODO
        pass

    # =================================================================================================
    # messaging wrappers to use in api class

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


if __name__ == "__main__":
    pass