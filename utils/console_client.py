#!/usr/bin/env python3

import time
import uuid
import sys, os
import argparse
from threading import Thread
import json

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
    parser = argparse.ArgumentParser(description="Plexus console client", epilog="And that's how you'd foo a bar")

    parser.add_argument("action", type=str, choices=["send", "list", "info"], help="name of action ")

    parser.add_argument("addr", type=str, help="in format: tcp://10.9.0.23:5566")
    parser.add_argument("node", type=str, help="name of node")
    parser.add_argument("device", type=str, help="name of device")
    parser.add_argument("command", type=str, help="name of command")
    parser.add_argument("args", type=str, help="string with params in it like this\n'{\"x\":12, \"y\":\"some_param\"}'")


    args = parser.parse_args()

    list_of_nodes1 = [
        {"name": "node1", "address": "tcp://10.9.0.23:5566"}
        ]

    client = PlexusUserApi(endpoint="tcp://10.9.0.1:5565", name="client", list_of_nodes=list_of_nodes1)

    # start user input parsing

    if args.action == "send": #and :
        msg_to_send = client.user_input_parse(
            addr=args.addr,
            node=args.node,
            device=args.device,
            command=args.command,
            raw_args=args.args
        )

        res = client.send_msg(msg_to_send)
        addr_decoded_, decoded_resp_ = Message.parse_zmq_msg(res)
        for k in decoded_resp_.keys():
            client.logger("{} - {}".format(k, decoded_resp_[k]))

    print("=================================================================================")
    # for n in list_of_nodes1:
    #     print(n)
    #
    #
    #     print("++++++++++++++++++++++++++++++ ogogogogogogogogo ++++++++++++++++++++++++++++++++")
    #     client.get_full_node_info(args.node)
    #     print("++++++++++++++++++++++++++++++ ogogogogogogogogo ++++++++++++++++++++++++++++++++")