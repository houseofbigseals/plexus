#!/usr/bin/env python3

import sys, os
import time
# from typing import Any
import zmq
import uuid
import json
# from zmq.eventloop.ioloop import IOLoop, PeriodicCallback
# from zmq.eventloop.zmqstream import ZMQStream
import datetime

try:
    from plexus.nodes.node import BaseNode, PeriodicCallback
    from plexus.nodes.message import Message
    from plexus.utils.logger import PrintLogger

except ModuleNotFoundError:
    from src.plexus.utils.logger import PrintLogger
    from src.plexus.nodes.node import BaseNode, PeriodicCallback
    from src.plexus.nodes.message import Message
    # here we trying to manually add our lib path to python path
    # abspath = os.path.abspath("../..")
    # sys.path.insert(0, "{}/utils".format(abspath))
    # sys.path.insert(0, "{}/nodes".format(abspath))



class PlexusUserApi:
    """
    all methods to remotely use and control desired group of nodes
    you have manually add correct exp network config
    and also manually add security sertificates

    """

    def __init__(self, endpoint: str, list_of_nodes: list):
        # super(PlexusUserApi, self).__init__(name=name, endpoint=endpoint, list_of_nodes=list_of_nodes)
        # base node preparations like creating sockets
        # preparations that user dont want to see
        self._endpoint = endpoint
        self.name = str(self._endpoint)
        self.logger = PrintLogger(self.name)
        self.logger("start init")

        # self.loop = None
        self.list_of_nodes = list_of_nodes
        self.network_state = dict()
        # Prepare our context and sockets
        self.context = zmq.Context.instance()

        # lets create your main socket with bind option
        self._socket = self.context.socket(zmq.ROUTER)
        self._socket.identity = "{}".format(self.name).encode('ascii')
        self.logger("{}".format(self.name).encode('ascii'))
        self._socket.bind(self._endpoint)
        # self.main_stream = ZMQStream(self._socket)
        # self.main_stream.on_recv_stream(self.reqv_callback)
        self.network_state = dict()
        self._sockets = dict()
        self.refresh_time = 10  # secs

        # then lets create lots of sockets for all other nodes from given list
        for n in self.list_of_nodes:
            if n != self.name:
                # create router socket and append it to self._sockets
                new_socket = self.context.socket(zmq.ROUTER)
                new_socket.identity = "{}".format(self.name).encode('ascii')
                # self.logger("{}".format(n["name"]).encode('ascii'))
                new_socket.connect(n)

                # new_stream = ZMQStream(new_socket)
                # new_stream.on_recv_stream(self.reqv_callback)

                # lets create big dict for every node in list, with
                self.network_state[n] = {"address": n,
                                                 "status": "unknown",
                                                 "last_msg_sent": None,
                                                 "last_msg_received": None,
                                                 "info": None,
                                                 "last_info_received": None,
                                                "socket": new_socket
                                         }

                self.logger("self network state: {}".format(self.network_state))

                # for now we will keep socket instance,  stream instance, last_time, and status
                # self._sockets[n["name"]] = {"socket": new_socket,
                #                             "address": n["address"],
                #                             "status": "not_started"}

                # self.logger(self._sockets[n["name"]])

        time.sleep(1)  # without that pause all stuff crushes

    def send_msg(self, msg_to_send: Message):
        """
        main function of all api
        send and blocking wait for response for selected timeout

        :return:
        """
        # find correct socket if it exists in self sockets table
        self.logger("try to send msg {} to {}".format(msg_to_send.msg_dict, msg_to_send.addr))
        if msg_to_send.addr in self.network_state.keys():
            sock = self.network_state[msg_to_send.addr]["socket"]
            self.logger("socket found")
        else:
            # it means that we have not such node in sockets table and we have to add it manually
            # TODO: for nao just raise error
            raise ConnectionError("no such node in self nodes list!")
            # # create router socket and append it to self._sockets
            # new_socket = self.context.socket(zmq.ROUTER)
            # new_socket.identity = "{}".format(self.name).encode('ascii')
            # # self.logger("{}".format(n["name"]).encode('ascii'))
            # new_socket.connect(n["address"])
            #
            # self._sockets[n["name"]] = {"socket": new_socket,
            #                             "address": n["address"],
            #                             "status": "not_started"}
        # self.logger(sock)
        msg = msg_to_send.create_zmq_msg()
        # self.logger(msg)
        try:
            # TODO check this
            sock.send_multipart(msg)   #, flags=zmq.NOBLOCK)
            self.logger("msg sent, lets wait for resp")
            answer = sock.recv_multipart()  #flags=zmq.NOBLOCK)
        except Exception as e:
            self.logger("problem with sending message: {}".format(e))
            answer = None
        # self.logger(answer)
        self.logger("we got resp: {}".format(answer))
        return answer


    # =================================================================================================
    # messaging primitive wrappers

    # def get_all_nodes_info(self):
    #     """
    #     returns list of all nodes from config with their addr and state
    #     :return:
    #     """
    #     self.logger("self network state: {}".format(self.network_state))
    #     return self.network_state

    def get_full_node_info(self, node_addr: str):
        """
        returns info about node with list of custom node commands and list of all devices and their state
        :return:
        """
        self.logger("get_full_node_info starts")
        info_message = Message(
            addr=str(node_addr),
            device=str(node_addr),
            command="info",
            msg_id=uuid.uuid4().hex,
            time_=time.time()
        )
        res = self.send_msg(info_message)
        addr_decoded_, decoded_resp_ = Message.parse_zmq_msg(res)
        self.logger("we got resp from node: {}".format(node_addr))
        # for i in decoded_resp_:
        #     self.logger((i, type(i)))
        # all_answer = decoded_resp_["data"]

        # self.logger("{} - {}".format("device", decoded_resp_["device"]))
        # self.logger("{} - {}".format("command", decoded_resp_["command"]))


        # add this info and its time to network state list
        if node_addr in self.network_state.keys():
            # update information
            self.network_state[node_addr]["info"] = decoded_resp_['data']
            self.network_state[node_addr]["last_info_received"] = time.time()
            self.network_state[node_addr]["last_msg_received"] = time.time()
        else:
            # we can add node to our list
            self.network_state[node_addr] = {"address": None,
                                                 "status": "new",
                                                 "last_msg_sent": None,
                                                 "last_msg_received": time.time(),
                                                 "info": decoded_resp_['data'],
                                                 "last_info_received": time.time()}
        self.logger("get_full_node_info ends")
        return addr_decoded_, decoded_resp_

    def get_full_device_info(self, node_addr, devname):
        """
        returns info about selected device with its commands and correspond params
        :return:
        """
        self.logger("get_full_device_info starts")
        # find node in network list
        if node_addr in self.network_state.keys():
            # lets check if info is actual
            if self.network_state[node_addr]["last_info_received"] and\
                    time.time() - self.network_state[node_addr]["last_info_received"] < self.refresh_time:
                # lets use this data
                data = self.network_state[node_addr]["info"]

                if devname in data["devices"]:
                    # this is request for existing device
                    self.logger("get_full_device_info ends cool")
                    return data["devices"][devname]

                elif devname == node_addr:
                    # this is request for system commands
                    self.logger("get_full_device_info ends cool with system commands")
                    return data["system_commands"]
                else:
                    self.logger("get_full_device_info ends with error because no such device")
                    return None
            else:
                # refresh and do this again
                self.get_full_node_info(node_addr)
                # and recursively run this method again
                self.logger("get_full_device_info ends with updating info end recursively runs itself")
                return self.get_full_device_info(node_addr, devname)

        else:
            self.logger("get_full_device_info ends wit error because no such node")
            return None


    # ===========================================================================================================
    # user args parser and other utils to make messaging more simple

    def user_input_parse(self, addr:str, node:str, device:str, command:str, raw_args:str):
        """

        IMPORTANT NOTE:
        raw_args value must be string like that:
        '{"arg1":34, "arg2":"some_param", ...}'
        so we can load it directly to dict from str

        simple method to parse and complete user commands from shell
        it uses own send method to communicate with other nodes
        return - prepared message
        """
        if node not in self.network_state.keys():
            # add it manually by addr and node name
            # and create socket for it
            try:
                # create router socket and append it to self._sockets
                new_socket = self.context.socket(zmq.ROUTER)
                new_socket.identity = "{}".format(self.name).encode('ascii')
                # self.logger("{}".format(n["name"]).encode('ascii'))
                new_socket.connect(addr)

                # lets create big dict for every node in list, with
                self.network_state[node] = {"address": addr,
                                            "status": "unknown",
                                            "last_msg_sent": None,
                                            "last_msg_received": None,
                                            "info": None,
                                            "last_info_received": None}

                self.logger("self network state updated: \n{}".format(self.network_state))

                # for now we will keep socket instance,  stream instance, last_time, and status
                self._sockets[node] = {"socket": new_socket,
                                            "address": addr,
                                            "status": "not_started"}


                # and create message object from that data
                msg_to_send = Message(
                    addr=node,
                    device=device,
                    command=command,
                    msg_id=uuid.uuid4().hex,
                    time_=time.time(),
                    data=json.loads(raw_args)
                )
                return msg_to_send


            except Exception as e:
                self.logger("Parsing error: \n{}".format(e))
                return "Parsing error: \n{}".format(e)
        else:
            # just create msg
            msg_to_send = Message(
                addr=node,
                device=device,
                command=command,
                msg_id=uuid.uuid4().hex,
                time_=time.time(),
                data=json.loads(raw_args)
            )
            return msg_to_send


if __name__ == "__main__":
    # list_of_nodes1 = [
    #     {"name": "node1", "address": "tcp://192.168.100.4:5566"},
    #     {"name": "node2", "address": "tcp://192.168.100.8:5567"},
    #     {"name": "node3", "address": "tcp://192.168.100.8:5568"}
    # ]
    list_of_nodes1 = [
        "tcp://10.9.0.23:5566",
        "tcp://10.9.0.21:5555"
        # {"name": "node1", "address": "tcp://10.9.0.23:5566"},
        # {"name": "node2", "address": "tcp://192.168.100.8:5567"},
        # {"name": "node3", "address": "tcp://192.168.100.8:5568"}
    ]
    user_api = PlexusUserApi(endpoint="tcp://10.9.0.21:5565", list_of_nodes=list_of_nodes1)

    print(user_api.get_full_node_info("tcp://10.9.0.21:5555"))
    print(user_api.get_full_device_info("tcp://10.9.0.21:5555", "tcp://10.9.0.21:5555"))

    # user_device = input("select device: ")


