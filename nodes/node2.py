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


try:
    from utils.logger import PrintLogger
    from nodes.message import Message
except ModuleNotFoundError:
    # here we trying to manually add our lib path to python path
    abspath = os.path.abspath("..")
    sys.path.insert(0, "{}/utils".format(abspath))
    sys.path.insert(0, "{}/nodes".format(abspath))
    from message import Message
    from logger import PrintLogger
    from message import Message


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
    def custom_request_parser(self, stream: ZMQStream, reqv_msg: Message):
        # here user can add custom parsing of received message
        pass

    @abstractmethod
    def custom_response_parser(self, stream: ZMQStream,  resp_msg: Message):
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
        self._sockets = dict()
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
                self._sockets[n["name"]] = {
                    "stream": new_stream,
                     "socket": new_socket,
                     "address": n["address"],
                     "status": "not_started"
                     }
                self.logger(self._sockets[n["name"]])

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

    def send(self, stream: ZMQStream, msg_to_send: Message):
        """handler for sending data to another node through local broker """
        # prepare msg
        msg = msg_to_send.create_zmq_msg()
        # then put its id to queue
        # self.store_awaiting_msg(msg_to_send)

        # also lets save last sent msg time in network config
        self.network_state[msg_to_send.addr]["last_msg_sent"] = time.time()
        self.logger("self network state: {}".format(self.network_state))

        # self.logger("msg to {} is {}".format(msg_to_send.addr, msg))
        # send msg
        stream.send_multipart(msg)

    def reqv_callback(self, stream: ZMQStream, reqv_msg: list):
        """base callback for all messages in all streams"""
        self.logger("reqv callback")
        self.logger("we got msg: {}".format(reqv_msg))
        # parse
        addr_decoded, decoded_dict = Message.parse_zmq_msg(reqv_msg)
        # self.logger([addr_decoded, decoded_dict])
        decoded_msg = Message.create_msg_from_addr_and_dict(addr_decoded=addr_decoded, decoded_dict=decoded_dict)
        self.logger(decoded_dict)

        # msg_id = msg_dict["id"]
        # command = msg_dict["command"]
        # device_name = msg_dict["device"]  # that is a str with device name
        # msg_data = msg_dict["data"]
        # msg_time = msg_dict["time"]

        # lets check if that node in our noeds list:
        if addr_decoded in self.network_state.keys():
            self.network_state[addr_decoded]["last_msg_received"] = time.time()
            self.logger("self network state: {}".format(self.network_state))
        else:
            self.logger("found new node by irs reqv: {}".format(addr_decoded))
            self.logger("we will add it to our network state container")
            # TODO mb it is good to add unknown node to our ping list?
            self.network_state[addr_decoded] = {"address": "unknown",
                                                # todo how to find addr? in form "tcp://192.168.100.8:5568"
                                                               "status": "unknown",
                                                               "last_msg_sent": None,
                                                               "last_msg_received": time.time()}

            self.logger("self network state: {}".format(self.network_state))

        # 1) lets check if it is response for one of our requests to another node
        self.logger(decoded_dict["command"])

        if decoded_dict["command"] == "RESP":
            # so we dont care about "device" field
            # it means that it it resp to us and we must not answer
            # answered_resp = self.extract_awaiting_msg(decoded_dict["msg_id"])
            self.logger("command RESP received in msg with id {}".format(decoded_dict["msg_id"]))
            self.logger("msg body is {}".format(decoded_dict))

            # here app must find original msg by its id and delete it from unanswered queue
            # also if it was resp for some system call, it must be handled here, before user parsing
            # print(stream, decoded_msg)
            self.system_resp_handler(stream=stream, resp_msg=decoded_msg)
            # and there - user parsing
            self.custom_response_parser(stream=stream, resp_msg=decoded_msg)

        # there is a list of system commands that we use under the hood
        # 2) check if it is command to node
        elif decoded_dict["device"] == self.name:
            # it means that msg was sent directly to node
            self.handle_system_msgs(stream, decoded_msg)

        # 3) check if it is command to one of our devices
        # let's check which device the message was sent to
        else:
            for device_ in self._devices:
                self.logger("msg device is {}".format(decoded_dict["device"]))
                if device_.name == decoded_dict["device"]:
                    self.logger("found requested device in our devices {}".format(device_.name))
                    # then call selected method on this device with that params
                    try:
                        result = device_.call(decoded_dict["command"], **decoded_dict["data"])
                        # encoded_result = pickle.dumps(result)
                        res_msg = Message(
                            addr=addr_decoded,
                            device=decoded_dict["device"],
                            command="RESP",
                            msg_id=decoded_dict["msg_id"],
                            time_=time.time(),
                            data=result
                        )
                        self.logger("try to send resp {}".format(res_msg))
                        self.send(stream, res_msg)
                    except Exception as e:
                        error_str = "error while calling device: {}".format(e)
                        self.logger(error_str)
                        res_msg = Message(
                            addr=addr_decoded,
                            device=decoded_dict["device"],
                            command="RESP",
                            msg_id=decoded_dict["msg_id"],
                            time_=time.time(),
                            data=error_str
                        )
                        self.logger("try to send resp wit error {}".format(res_msg))
                        self.send(stream, res_msg)

            # this is shit and we dont want to handle it
            self.logger("command {} is not system, trying to use user handler".format(decoded_dict["command"]))
            # 5) may be user want to handle it somehow
            self.custom_request_parser(stream, decoded_msg)

    def handle_system_msgs(self, stream, reqv_msg: Message):
        """handler to base commands, those can be sent to every node by another node"""
        if reqv_msg.command == "INFO":
            # it means that it it reqv to us and we must answer
            # in answer we need to send all info about node and its devices
            self.logger("command INFO received")
            info = {
                "name": self.name,
                "status": self.status,
                "devices": self._devices
            }
            # to_addr = from_addr
            # self.send(stream=stream,
            #     addr=to_addr,
            #     device=self.name,
            #     command="RESP",
            #     msg_id=msg_dict["id"],
            #     data=info)
            res_msg = Message(
                addr=reqv_msg.addr,
                device=reqv_msg.device,
                command="RESP",
                msg_id=reqv_msg.msg_id,
                time_=time.time(),
                data=info
            )
            self.send(stream, res_msg)

        if reqv_msg.command == "PING":
            # it means that it it reqv to us and we must answer
            # in answer we need to send all info about node and its devices
            self.logger("command PING received")
            res_msg = Message(
                addr=reqv_msg.addr,
                device=reqv_msg.device,
                command="RESP",
                msg_id=reqv_msg.msg_id,
                time_=time.time(),
                data="ACK"
            )
            self.send(stream, res_msg)
            # we have to send resp with standard info about this node and its devices

    def on_ping_timer(self):
        # method to ping other sockets
        self.logger("try to send ping")
        for s in self._sockets.keys():
            # self._sockets[n["name"]] = {
            #     "stream": new_stream,
            #     "socket": new_socket,
            #     "address": n["address"],
            #     "status": "not_started"
            # }
            ping_msg = Message(
                addr=s,
                device=s,  # here addr is name and device is name too
                command="PING",
                msg_id=uuid.uuid1(),
                time_=time.time(),
                data=b''
            )
            # print(self._sockets[s]["stream"])
            self.send(stream=self._sockets[s]["stream"], msg_to_send=ping_msg)

    # def store_awaiting_msg(self, resp_msg: Message):
    #     """ user can override this method if needs"""
    #     # TODO

    # def extract_awaiting_msg(self, resp_msg: Message):
    #     """ user can override this method if needs"""
    #     # TODO
    #     msg = Message.create_msg_from_addr_and_dict("pass", dict())
    #     return msg

    def system_resp_handler(self, stream: ZMQStream, resp_msg: Message):
        """ user can override this method if needs"""
        # TODO
        pass



if __name__ == "__main__":
    pass