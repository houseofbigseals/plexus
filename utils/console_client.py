#!/usr/bin/env python3

import time
import uuid
import sys, os
import argparse
from threading import Thread

# custom path imports
try:
    from nodes.node2 import BaseNode, PeriodicCallback, Message
    from utils.console_client_api import PlexusUserApi

except Exception:
    # here we trying to manually add our lib path to python path
    abspath = os.path.abspath("..")
    # print(abspath)
    sys.path.insert(0, "{}/nodes".format(abspath))
    sys.path.insert(0, "{}/devices".format(abspath))
    sys.path.insert(0, "{}/utils".format(abspath))
    # print(sys.path)
    from message import Message
    from console_client_api import PlexusUserApi




if __name__ == '__main__':

    list_of_nodes1 = [
        {"name": "node1", "address": "tcp://10.9.0.23:5566"}
        ]

    client = PlexusUserApi(endpoint="tcp://10.9.0.1:5565", name="client", list_of_nodes=list_of_nodes1)

    parser = argparse.ArgumentParser(description="Plexus console client")
    print("==============================================================\navailable nodes are:")
    for n in list_of_nodes1:
        print(n)
    parser.add_argument("-n", dest="node_name", required=True, type=str)

    args = parser.parse_args()

    print("++++++++++++++++++++++++++++++ ogogogogogogogogo ++++++++++++++++++++++++++++++++")
    client.get_full_node_info(args.node_name)
    print("++++++++++++++++++++++++++++++ ogogogogogogogogo ++++++++++++++++++++++++++++++++")