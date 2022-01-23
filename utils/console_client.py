#!/usr/bin/env python3

import time
import uuid
import sys, os
import argparse
import textwrap
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


def print_intro_help():
    return "Hello \nThis is a plexus console client. Version 0.0.1, GPLv3 license." \
           "\nThere are two commands: send and info.\n" \
           "Print send -h or info -h for more information"

def send_help():
    return "Sends command to selected node via ZMQ sockets and returns answer. \n" \
           "Using: addr node device command args. Use this params:\n\n" \
           "\taddr: string like in format: tcp://10.9.0.23:5566\n" \
           "\tnode: string with node name\n" \
           "\tdevice: string with device name\n" \
           "\tcommand: string with device name\n" \
           "\targs: args string must be like this: '{\"x\":12, \"y\":\"some_param\"}'\n\n" \
           "for example:\n" \
           "tcp://10.9.0.23:5566 node_name device_name some_command '{\"x\":12, \"y\":\"some_param\"}' "

def info_help():
    return "Returns info about selected address of remote machine, node, device or command\n" \
           "Different nodes can have similar device names, same with different remote machines,\n" \
           "so you have to clarify your request. For example, if you need info about specific node\ndo like this:\n" \
           "\n\tinfo tcp://10.9.0.23:5566 node_name\n\n" \
           "And if you need info about specific command in specific device do like this:\n" \
           "\n\tinfo tcp://10.9.0.23:5566 node_name device_name command_name\n\n"

if __name__ == '__main__':
    args = dict()
    flag = "undefined"

    if len(sys.argv) == 1 or sys.argv[1] == "-h":
        print(print_intro_help())

    else:
        try:
            if sys.argv[1] == "send":
                if sys.argv[2] == "-h":
                    print(send_help())
                else:
                    # for now no any checking of user input
                    args["addr"] = sys.argv[2]
                    args["node"] = sys.argv[3]
                    args["device"] = sys.argv[4]
                    args["command"] = sys.argv[5]
                    args["args"] = sys.argv[6]
                    flag = "send"

            if sys.argv[1] == "info":
                if sys.argv[2] == "-h":
                    print(info_help())
                else:
                    if len(sys.argv) == 3:
                        # it must be request for addr info
                        args["addr"] = sys.argv[2]
                        flag = "addr_info"
                    if len(sys.argv) == 4:
                        # it must be request for node info
                        args["addr"] = sys.argv[2]
                        args["node"] = sys.argv[3]
                        flag = "node_info"
                    if len(sys.argv) == 5:
                        # it must be request for node info
                        args["addr"] = sys.argv[2]
                        args["node"] = sys.argv[3]
                        args["device"] = sys.argv[4]
                        flag = "device_info"
                    if len(sys.argv) == 6:
                        # it must be request for node info
                        args["addr"] = sys.argv[2]
                        args["node"] = sys.argv[3]
                        args["device"] = sys.argv[4]
                        args["command"] = sys.argv[5]
                        flag = "command_info"

        except Exception as e:
            print("Incorrect input. Try -h option")
            # print("incorrect input : {}".format(e))

    list_of_nodes1 = [
        # {"name": "node1", "address": "tcp://10.9.0.23:5566"}
        # {"name": "node1", "address": "tcp://10.9.0.23:5566"}
        {"name": "node1", "address": "tcp://127.0.0.1:5566"}
        ]

    print(args)
    # args = parser.parse_args()
    # client_addr = "tcp://10.9.0.21:5565"
    # client_addr = "tcp://10.9.0.1:5565"
    # client_addr = "tcp://192.168.100.5:5565"
    client_addr = "tcp://127.0.0.1:5555"

    if flag == "send":
        client = PlexusUserApi(endpoint=client_addr, name="client", list_of_nodes=list_of_nodes1)

        # if args.action == "send": #and :
        msg_to_send = client.user_input_parse(
            addr=args["addr"],
            node=args["node"],
            device=args["device"],
            command=args["command"],
            raw_args=args["args"]
        )
        res = client.send_msg(msg_to_send)
        addr_decoded_, decoded_resp_ = Message.parse_zmq_msg(res)
        for k in decoded_resp_.keys():
            client.logger("{} - {}".format(k, decoded_resp_[k]))
    elif flag == "addr_info":

        res = list()
        for n in list_of_nodes1:
            if args["addr"] == n["address"]:
                res.append(n)
        print("there is {} nodes on this addr. \n There is a list: \n".format(len(res)))
        for i in res:
            print(i)
        # if len(sys.argv) == 2:
    elif flag == "node_info":
        client = PlexusUserApi(endpoint=client_addr, name="client", list_of_nodes=list_of_nodes1)
        addr_decoded_, decoded_resp_ = client.get_full_node_info(args["node"])
        raw_info = decoded_resp_["data"]["devices"]
        print(" ")
        print("name: {}".format(decoded_resp_["data"]["name"]))
        print("info: {}".format(decoded_resp_["data"]["annotation"]))
        print("status: {}".format(decoded_resp_["data"]["status"]))
        print(" ")
        print("List of devices:\n")
        for i in raw_info.keys():
            print(f"\t{i}:  {raw_info[i]['annotation']}")
        print(" ")

    elif flag == "device_info":
        client = PlexusUserApi(endpoint=client_addr, name="client", list_of_nodes=list_of_nodes1)
        raw_info = client.get_full_device_info(args["node"], args["device"])
         # = decoded_resp_
        if args["node"] != args["device"]:
            print(f"{args['device']} device info:\n")
            print(f"\tname: {raw_info['name']}")
            print(f"\tinfo: {raw_info['annotation']}")
            print(f"\tstatus: {raw_info['status']}")

            print(f"\nAvailable commands for {raw_info['name']} device:\n")
            for c in raw_info["commands"].keys():
                # print(f"\t{c} : {raw_info['commands'][c]}")
                print(f"\t{c} : {raw_info['commands'][c]['annotation']}")
            print(" ")
        else:
            print(f"{args['device']} system commands info:\n")
            for c in raw_info.keys():
                # print(f"\t{c} : {raw_info['commands'][c]}")
                print(f"\t{c} : {raw_info[c]['annotation']}")
            print(" ")
        # print(client.get_full_device_info(args["node"], args["device"]))


    elif flag == "command_info":
        client = PlexusUserApi(endpoint=client_addr, name="client", list_of_nodes=list_of_nodes1)
        raw_info = client.get_full_device_info(args["node"], args["device"])
        if args["node"] != args["device"]:
            print(raw_info)
            data = raw_info['commands'][args['command']]
            print(data)
            print(args)
            # [args['command']]

            print(f"\n{args['command']} command info:\n")
            print(f"\tname: {data['name']}")
            print(f"\tinfo: {data['annotation']}")
            # print(f"\tstatus: {data['status']}")
            print(f"\nAvailable input args for {args['command']} command:\n")

            if data['input_kwargs']:
                for a in data['input_kwargs'].items():
                    print(f"\t{a}")
            else:
                print("\tno input kwargs")
            print(f"\nAvailable output args for {args['command']} command:\n")

            if data['output_kwargs']:
                for a in data['output_kwargs'].items():
                    print(f"\t{a}")
            else:
                print("\tno output kwargs")

        else:
            print(f"{args['device']} system commands info:\n")
            print(f"\n{args['command']} command info:\n")

            data = raw_info[args['command']]
            
            print(f"\tname: {data['name']}")
            print(f"\tinfo: {data['annotation']}")
            # print(f"\tstatus: {data['status']}")
            print(f"\nAvailable input args for {args['command']} command:\n")

            if data['input_kwargs']:
                for a in data['input_kwargs'].items():
                    print(f"\t{a}")
            else:
                print("\tno input kwargs")
            print(f"\nAvailable output args for {args['command']} command:\n")

            if data['output_kwargs']:
                for a in data['output_kwargs'].items():
                    print(f"\t{a}")
            else:
                print("\tno output kwargs")

        # print(info[args["command"]])

        # print("=================================================================================")
        # for n in list_of_nodes1:
        #     print(n)
        #
        #
        #     print("++++++++++++++++++++++++++++++ ogogogogogogogogo ++++++++++++++++++++++++++++++++")
        #     client.get_full_node_info(args.node)
        #     print("++++++++++++++++++++++++++++++ ogogogogogogogogo ++++++++++++++++++++++++++++++++")