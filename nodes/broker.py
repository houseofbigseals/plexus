import random
import time
import zmq

from zmq.eventloop.ioloop import IOLoop, PeriodicCallback
from zmq.eventloop.zmqstream import ZMQStream
from multiprocessing import Process
from datetime import datetime
import os, sys

try:
    from utils.config_parser import ConfigParser
except ModuleNotFoundError:
    # here we trying to manually add our lib path to python path
    abspath = os.path.abspath("..")
    sys.path.insert(0, "{}/utils".format(abspath))
    from config_parser import ConfigParser


class BrokerNode(Process):
    """

    """
    def __init__(self, name: str, is_daemon: bool, config: ConfigParser):
        Process.__init__(self, daemon=is_daemon)
        print("BROKER: start init")
        # lets parse config
        self.name = ConfigParser
        self.front_endpoint = front_endpoint
        # Prepare our context and sockets
        self.context = zmq.Context()
        self.reqv_socket = None
        self.resp_socket = None
        self.ping_timer_interval = 1000
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
        print("BROKER: fast async timer works again! - {}".format(datetime.now()))
        time.sleep(1)

    def on_timer2(self):
        """Method called on timer expiry.
        :rtype: None
        """
        print("BROKER: slow async timer works again!- {}".format(datetime.now()))
        time.sleep(5)


    def run(self):
        """
        this method will be called when the broker start() function is called by user
        :return:
        """
        print("BROKER: start run")
        self.reqv_socket = self.context.socket(zmq.ROUTER)
        self.reqv_socket.identity = (u"broker").encode('ascii')
        self.reqv_socket.bind(self.front_endpoint)
        self.main_stream = ZMQStream(self.reqv_socket)
        self.main_stream.on_recv(self.reqv_callback)
        # self.main_stream.on_send(self.resp_callback)

        # start timer
        self.check_timer = PeriodicCallback(self.on_timer, 1000)
        self.check_timer2 = PeriodicCallback(self.on_timer2, 5000)
        self.check_timer.start()
        self.check_timer2.start()

        self.loop = IOLoop.current()  # do we need it ?
        print("BROKER: go to loop")
        self.loop.start()


if __name__ == "__main__":
    # example:

    exp_config = {
        "experiment": "test1",
        "addresses":
            {
                "pc1": "tcp://192.168.100.4:5566",
                "pc2": "tcp://192.168.100.8:5566"
            }
        # pc_name : tcp addr and port
        # every broker must know own pc name
    }
    c = ConfigParser()
    c.init_from_dict(exp_config)
    c.show_pretty_graph()

    broker = BrokerNode(name="pc1", config=c, is_daemon=True)
    broker.start()
    broker.join()
