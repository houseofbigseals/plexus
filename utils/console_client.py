#!/usr/bin/env python3

import time
import uuid
import sys, os
from threading import Thread

# custom path imports
try:
    from nodes.node2 import BaseNode, PeriodicCallback, Message
    from utils.console_client_api import PlexusUserApi

except Exception:
    # here we trying to manually add our lib path to python path
    abspath = os.path.abspath("..")
    print(abspath)
    sys.path.insert(0, "{}/nodes".format(abspath))
    sys.path.insert(0, "{}/devices".format(abspath))
    sys.path.insert(0, "{}/utils".format(abspath))
    print(sys.path)
    from message import Message
    from console_client_api import PlexusUserApi




if __name__ == '__main__':

    list_of_nodes1 = [
        {"name": "node1", "address": "tcp://10.9.0.23:5566"}
        ]

    client = PlexusUserApi(endpoint="tcp://10.9.0.21:5565", name="client", list_of_nodes=list_of_nodes1)

    print("\nhi\navailable nodes are:")
    for n in list_of_nodes1:
        print(n)

    # user_node = input("select node: ")
    # user_node = "node1"
    # user_node = input("select node: ")
    # print(len(user_node), type(user_node))
    #
    # print("your input: {}".format(user_node))

    # client.get_full_node_info("node1")
    # client.get_full_node_info(user_node)


    # def pprr():
    #     while True:
    #         time.sleep(1)
    # df = Thread(target= pprr, daemon=True)
    # df.start()


    print("++++++++++++++++++++++++++++++ ogogogogogogogogo ++++++++++++++++++++++++++++++++")
    client.get_full_node_info('node1')
    print("++++++++++++++++++++++++++++++ ogogogogogogogogo ++++++++++++++++++++++++++++++++")