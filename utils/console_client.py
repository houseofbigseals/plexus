#!/usr/bin/env python3

import argparse, sys, os
import time
from typing import Any

try:
    from utils.logger import PrintLogger
    from nodes.node2 import BaseNode, PeriodicCallback
except ModuleNotFoundError:
    # here we trying to manually add our lib path to python path
    abspath = os.path.abspath("..")
    sys.path.insert(0, "{}/utils".format(abspath))
    sys.path.insert(0, "{}/nodes".format(abspath))
    from node2 import BaseNode, PeriodicCallback, uuid
    from logger import PrintLogger


class PlexusUserApi(BaseNode):
    """
    all methods to remotely use and control desired group of nodes
    you have manually add correct exp network config
    and also manually add security sertificates

    """

    # =================================================================================================
    # wrappers for abstract methods from base node

    def custom_preparation(self):
        # here user must do all preparations
        # also create and start all PeriodicCallback tasks
        # like that:
        # self.check_timer = PeriodicCallback(self.on_timer, self.period)
        # self.check_timer.start()
        pass

    def custom_request_parser(self, stream, from_addr: str, msg_dict: dict):
        # here user can add custom parsing of received message
        pass

    def custom_response_parser(self, stream,  from_addr: str, msg_dict: dict, reqv_msg: Any):
        # here user can add custom parsing of received answer for his message
        pass

    def __init__(self, endpoint: str, name: str, list_of_nodes: list):
        super(PlexusUserApi, self).__init__(name=name, endpoint=endpoint, list_of_nodes=list_of_nodes)
        pass


    def send_msg(self, node_name, device_name, command, args):
        """

        :param node_name:
        :param device_name:
        :param command:
        :param args:
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


