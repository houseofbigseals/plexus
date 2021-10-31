import random
import time
import zmq

from zmq.eventloop.ioloop import IOLoop, PeriodicCallback
from zmq.eventloop.zmqstream import ZMQStream
from multiprocessing import Process


class BrokerNode(Process):
    def __init__(self, front_endpoint, is_daemon):
        Process.__init__(self, daemon=is_daemon)
        print("BROKER: start init")
        self.front_endpoint = front_endpoint
        # self.back_port = back_port
        # Prepare our context and sockets
        self.context = zmq.Context()
        self.reqv_socket = None
        self.resp_socket = None
        self.timer_interval = 1000
        self.check_timer = None
        self.main_stream = None
        print("BROKER: end init")

    def reqv_callback(self, msg):
        print("BROKER: get msg {}".format(msg))
        from_addr = msg[0]  # was added automatically
        to_addr = msg[2]
        msg_body = msg[4]
        msg_to_send = [to_addr, b'', from_addr, b'', msg_body]
        print("BROKER: send msg {}".format(msg_to_send))
        self.main_stream.send_multipart(msg_to_send)

    # def resp_callback(self, msg):
    #     #self.main_stream.send_multipart(msg)
    #     print("BROKER: send msg {}".format(msg))

    def on_timer(self):
        """Method called on timer expiry.
        :rtype: None
        """
        print("BROKER: async timer works again!")


    def run(self):
        print("BROKER: start run")
        self.reqv_socket = self.context.socket(zmq.ROUTER)
        self.reqv_socket.identity = (u"broker").encode('ascii')
        self.reqv_socket.bind(self.front_endpoint)
        self.main_stream = ZMQStream(self.reqv_socket)
        self.main_stream.on_recv(self.reqv_callback)
        # self.main_stream.on_send(self.resp_callback)

        # start timer
        self.check_timer = PeriodicCallback(self.on_timer, 2000)
        self.check_timer.start()

        self.loop = IOLoop.current()  # do we need it ?
        print("BROKER: go to loop")
        self.loop.start()