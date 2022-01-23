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
    def custom_request_parser(self, from_addr: str, msg_dict: dict):
        # here user can add custom parsing of received message
        pass

    @abstractmethod
    def custom_response_parser(self, from_addr: str, msg_dict: dict, reqv_msg: Any):
        # here user can add custom parsing of received answer for his message
        pass

    # ===============================================================================

    def __init__(self, endpoint: str, broker_name: str, name: str, is_daemon: bool = True):
        """

        :param endpoint:
        :param broker_name:
        :param name:
        :param is_daemon:
        """
        Process.__init__(self, daemon=is_daemon)
        self._kill_flag = False
        self.name = name
        self.logger = PrintLogger(self.name)
        self.logger("start init")
        self._endpoint = endpoint
        # container to keep all local devices in one place
        self._devices = []
        self._broker = broker_name
        self.loop = None

        # Prepare our context and sockets
        self.context = zmq.Context()
        self._socket = None
        self.main_stream = None
        self.ping_timer = None
        self.logger("end init")
        self.status = "not_started"
        self.ping_period = 1000

        self._description = "abstract base node"

    # ========= tech methods, those must not be redefined by user ==========

    def run(self):
        """this method calls when user do node.start()"""
        # base node preparations like creating sockets
        # preparations that user dont want to see
        self.logger("start run")
        self._socket = self.context.socket(zmq.ROUTER)
        self._socket.identity = u"{}".format(self.name).encode('ascii')
        self._socket.connect(self._endpoint)
        self.main_stream = ZMQStream(self._socket)
        self.main_stream.on_recv(self.reqv_callback)
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

    def send(self, addr: str, device: str, command: str, msg_id: uuid, data: Any):
        """handler for sending data to another node through local broker """
        # prepare msg
        msg_dict = dict()
        msg_dict["device"] = device
        msg_dict["command"] = command
        msg_dict["id"] = msg_id
        msg_dict["time"] = time.time()
        msg_dict["data"] = data
        msg_encoded = pickle.dumps(msg_dict)
        msg = [self._broker.encode('ascii'), b'', addr.encode('ascii'), b'', msg_encoded]
        # then put its id to queue
        self.store_awaiting_msg(msg)
        self.logger("msg to {} is {}".format(addr, msg))
        # send msg
        self.main_stream.send_multipart(msg)

    def reqv_callback(self, msg):
        """base callback for all messages"""
        self.logger("reqv callback")
        self.logger("we got msg: {}".format(msg))
        # parse
        broker = msg[0]
        empty = msg[1]
        from_addr = msg[2]
        empty = msg[3]
        msg_body = msg[4]
        msg_dict = pickle.loads(msg_body)

        msg_id = msg_dict["id"]
        command = msg_dict["command"]
        device_name = msg_dict["device"]  # that is a str with device name
        msg_data = msg_dict["data"]
        msg_time = msg_dict["time"]

        # 1) lets check if it is response for one of our requests to another node

        if command == "RESP":
            # so we dont care about "device" field
            # it means that it it resp to us and we must not answer
            answered_resp = self.extract_awaiting_msg(msg_id)
            self.logger("command RESP received in msg with id {}".format(msg_id))
            self.logger("msg body is {}".format(msg_dict))
            # here app must find original msg by its id and delete it from unanswered queue
            # also if it was resp for some system call, it must be handled here, before user parsing
            self.system_resp_handler(from_addr, msg_dict, answered_resp)
            # and there - user parsing
            self.custom_response_parser(from_addr, msg_dict, answered_resp)

        # there is a list of system commands that we use under the hood
        # 2) check if it is command to node
        elif device_name == self.name:
            # it means that msg was sent directly to node
            self.handle_system_msgs(from_addr, msg_dict)

        # 3) check if it is command to one of our devices
        # let's check which device the message was sent to
        else:
            for device_ in self._devices:
                if device_.name == device_name:
                    # then call selected method on this device with that params
                    try:
                        result = device_.call(command, **msg_data)
                        encoded_result = pickle.dumps(result)
                        self.send(from_addr, device_name, "RESP", msg_id, encoded_result)
                    except Exception as e:
                        error_str = "error while calling device: {}".format(e)
                        self.logger(error_str)
                        self.send(from_addr, device_name, "RESP", msg_id, pickle.dumps(error_str))

            # this is shit and we dont want to handle it
            self.logger(" command {} is not system, trying to use user handler".format(self.name, command))
            # 5) may be user want to handle it somehow
            self.custom_request_parser(from_addr, msg_dict)

    def handle_system_msgs(self, from_addr, msg_dict):
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
            # we have to send resp with standard info about this node and its devices
            self.send(addr=to_addr,
                      device=self.name,
                      command="RESP",
                      msg_id=msg_dict["id"],
                      data="ACK".encode())

    def on_ping_timer(self):
        # method to ping broker
        #TODO add this feature to broker too
        # self.logger("try to send ping")
        self.send(self._broker, self._broker, "PING", uuid.uuid1(), b'')



    def store_awaiting_msg(self, msg: Any):
        # TODO
        pass

    def extract_awaiting_msg(self, msg_id: Any):
        # TODO
        msg = None
        return msg

    def system_resp_handler(self, from_addr: str, msg_dict: dict, reqv_msg: Any):
        # TODO
        pass

    # def find_broker(self):
    #     # returns broker name as string to send messages later
    #     # if no response from broker - raise exception
    #     # how to find broker?
    #     # TODO for now we cannot find it)
    #
    #     return "broker"





if __name__ == "__main__":
    pass


    # def on_timer(self):
    #     print("USER_{}: on timer called, so i will send msg".format(self.name))
    #     broker_addr = (u"Broker-reqv").encode('ascii')
    #
    #     to_addr = u"USER_{}".format(random.randint(1, 4)).encode('ascii')
    #     msg_body = "REQV from USER_{} to {}: you are gay".format(self.name, to_addr).encode('ascii')
    #     msg = [broker_addr, b'', to_addr, b'', msg_body]
    #     self.main_stream.send_multipart(msg)