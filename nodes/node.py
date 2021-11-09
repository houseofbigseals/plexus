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


class UserNode(ABC, Process):
    """

    """

    # ========= abstract methods, those must be redefined by user ==========
    @abstractmethod
    def user_run(self):
        # here user must do all preparations
        # also create and start all PeriodicCallback tasks
        # like that:
        # self.check_timer = PeriodicCallback(self.on_timer, self.period)
        # self.check_timer.start()
        pass

    @abstractmethod
    def user_request_parser(self, from_addr, command, msg_dict):
        # here user can add custom parsing of received message
        pass

    @abstractmethod
    def user_response_parser(self, from_addr, command, msg_dict):
        # here user can add custom parsing of received answer for his message
        pass

    def __init__(self, endpoint, name, is_daemon):

        Process.__init__(self, daemon=is_daemon)
        self.name = name
        self.logger = PrintLogger(self.name)
        self.logger("start init")
        self._endpoint = endpoint
        # container to keep all local devices in one place
        self._devices = []

        # Prepare our context and sockets
        self.context = zmq.Context()
        self._socket = None
        self.main_stream = None
        self.logger("end init")

        self._description = "base node"

    # ========= tech methods, those must not be redefined by user ==========
    def parse_msg(self, msg):
        try:
            broker = msg[0]
            empty = msg[1]
            from_addr = msg[2]
            empty = msg[3]
            msg_body = msg[4]
            msg_dict = pickle.loads(msg_body)
            command = msg_dict["command"]
            # msg_id = msg_dict["id"]
            # msg_time = msg_dict["time"]
            # msg_data = msg_dict["data"]
            return from_addr, command, msg_dict
        except Exception as e:
            self.logger("error while parsing: {}".format(e))

    # default handlers for not-user commands
    def on_start(self):
        pass

    def on_stop(self):
        pass

    def on_info(self):
        #
        pass

    # system methods
    def send(self, addr, command, msg_id, data):
        # handler for sending data to another node
        # prepare msg
        msg_dict = dict()
        msg_dict["command"] = command
        msg_dict["id"] = msg_id
        msg_dict["time"] = time.time()
        msg_dict["data"] = data
        msg_encoded = pickle.dumps(msg_dict)
        msg = [self.broker.encode('ascii'), b'', addr, b'', msg_encoded]
        self.logger("msg to {} is {}".format(addr, msg_dict))
        # send msg
        self.main_stream.send_multipart(msg)

    def ping(self):
        # method to ping broker
        self.send(self.broker, "PING", uuid.uuid1(), b'')

    def find_broker(self):
        # TODO
        return "broker"

    def prepare_run(self):
        # preparations that user dont want to see
        self.logger("start run")
        self._socket = self.context.socket(zmq.ROUTER)
        self._socket.identity = u"{}".format(self.name).encode('ascii')
        self._socket.connect(self._endpoint)
        self.main_stream = ZMQStream(self._socket)
        self.main_stream.on_recv(self.reqv_callback)
        self.broker = self.find_broker()

    def run(self):
        # this method calls when user do node.start()
        self.prepare_run()
        self.user_run()

        self.loop = IOLoop.current()  # do we need it ?
        self.logger("go to loop")
        self.loop.start()

    def reqv_callback(self, msg):
        self.logger(" reqv callback")
        self.logger("we got msg: {}".format(msg))
        from_addr, command, msg_dict = self.parse_msg(msg)
        msg_id = msg_dict["id"]
        # there is a list of system commands that are used under the hood
        if command == "INFO":
            # it means that it it reqv to us and we must answer
            self.logger("command INFO received")
            to_addr = from_addr
            
            self.send(to_addr, "RESP", msg_id, "ACK")


        elif command == "RESP":
            # it means that it it resp to us and we must not answer
            self.logger("command RESP received for msg with id {}".format(msg_id))
            self.logger("msg body is {}".format(msg_dict))
            # here app must find original msg by its id and delete it from unanswered queue
            # also if it was resp for some system call, it must be handled here, before user parsing
            self.user_response_parser(from_addr, command, msg_dict)

        else:
            # this is shit and we dont want to handle it
            self.logger(" command {} is not system, trying to use users handler".format(self.name, command))
            self.user_request_parser(from_addr, command, msg_dict)





    # def on_timer(self):
    #     print("USER_{}: on timer called, so i will send msg".format(self.name))
    #     broker_addr = (u"Broker-reqv").encode('ascii')
    #
    #     to_addr = u"USER_{}".format(random.randint(1, 4)).encode('ascii')
    #     msg_body = "REQV from USER_{} to {}: you are gay".format(self.name, to_addr).encode('ascii')
    #     msg = [broker_addr, b'', to_addr, b'', msg_body]
    #     self.main_stream.send_multipart(msg)