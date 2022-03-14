import time
import uuid
import zmq

from zmq.eventloop.ioloop import IOLoop, PeriodicCallback
from zmq.eventloop.zmqstream import ZMQStream
from multiprocessing import Process
from abc import ABC, abstractmethod

try:
    from plexus.nodes.message import Message
    from plexus.utils.logger import PrintLogger
    from plexus.nodes.command import Command

except ModuleNotFoundError:
    # here we trying to manually add our lib path to python path
    # abspath = os.path.abspath("../..")
    # sys.path.insert(0, "{}/utils".format(abspath))
    # sys.path.insert(0, "{}/nodes".format(abspath))
    from src.plexus.utils.logger import PrintLogger
    from src.plexus.nodes.message import Message
    from src.plexus.nodes.command import Command



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

    def custom_request_parser(self, stream: ZMQStream, reqv_msg: Message):
        # here user can add custom parsing of received message
        pass

    def custom_response_parser(self, stream: ZMQStream,  resp_msg: Message):
        # here user can add custom parsing of received answer for his message
        pass

    # ===============================================================================

    def __init__(self, endpoint: str, name: str, list_of_nodes: list, is_daemon: bool = True):
        """
        :param list_of_nodes: must be list with dicts like
        [
        {"name": "node1", "address": "tcp://192.168.100.4:5566"},
        ...
        {"name": "node100", "address": "tcp://192.168.100.4:5567"}
        ]
        :param endpoint:
        :param name:
        :param is_daemon:
        """
        Process.__init__(self, daemon=is_daemon)
        self.name = name
        self.logger = PrintLogger(self.name)
        self.logger("start init")
        self._endpoint = endpoint
        # container to keep all local devices in one place
        self._devices = list()
        self.loop = None
        self.list_of_nodes = list_of_nodes
        self.network_state = dict()

        self.info = None  # by default no devices in node, so None is info
        # we can update info later
        # for example - in run()
        # self.custom_commands = list()  # by default there is no custom commands

        # Prepare our context and sockets
        self.context = zmq.Context()
        self._socket = None
        self.main_stream = None
        self.ping_timer = None
        self.logger("end init")
        self._status = "not_started"
        self.ping_period = 1000
        self._sockets = dict()
        self._annotation = "abstract base node"

        info_command = Command(
            name="info",
            annotation="full info about node and its devices",
            output_kwargs={"info_dict": "dict"}
        )

        ping_command = Command(
            name="ping",
            annotation="simple ping",
            output_kwargs={"ack_str": "str"}
        )

        # start_command = Command(
        #     name="start",
        #     annotation="command to do some mystical preparation work like low-level calibration",
        #     output_kwargs={"ack_str": "str"}
        # )
        #
        # stop_command = Command(
        #     name="stop",
        #     annotation="command to do some mystical pausing work like closing valves or smth",
        #     output_kwargs={"ack_str": "str"}
        # )
        #
        kill_command = Command(
            name="kill",
            annotation="command to fully stop work of this process",
            output_kwargs={"ack_str": "str"}
        )
        self.system_commands = [info_command, ping_command, kill_command]

    # ========= tech methods, those must not be redefined by user ==========

    def run(self):
        """this method calls when user do node.start()"""
        # base node preparations like creating sockets
        # preparations that user dont want to see
        self.logger("start run")
        # lets create your main socket with bind option
        self._socket = self.context.socket(zmq.ROUTER)
        self._socket.identity = "{}".format(self.name).encode('ascii')
        self.logger("{}".format(self.name).encode('ascii'))
        self._socket.bind(self._endpoint)
        self.main_stream = ZMQStream(self._socket)
        self.main_stream.on_recv_stream(self.reqv_callback)
        self.network_state = dict()

        # then lets create lots of sockets for all other nodes from given list
        for n in self.list_of_nodes:
            if n["name"] != self.name:
                # create router socket and append it to self._sockets
                new_socket = self.context.socket(zmq.ROUTER)
                new_socket.identity = "{}".format(self.name).encode('ascii')
                self.logger("{}".format(n["name"]).encode('ascii'))
                new_socket.connect(n["address"])
                new_stream = ZMQStream(new_socket)
                new_stream.on_recv_stream(self.reqv_callback)
                # lets create big dict for every node in list, with
                self.network_state[n["name"]] = {"address": n["address"],
                                                 "status": "unknown",
                                                 "last_msg_sent": None,
                                                 "last_msg_received": None}
                self.logger("self network state: {}".format(self.network_state))

                # for now we will keep socket instance,  stream instance, last_time, and status
                self._sockets[n["name"]] = {
                    "stream": new_stream,
                     "socket": new_socket,
                     "address": n["address"],
                     "status": "not_started"
                     }
                self.logger(self._sockets[n["name"]])

        self.ping_timer = PeriodicCallback(self.on_ping_timer, self.ping_period)
        #self.death_timer = PeriodicCallback(self.on_death_timer, self.ping_period)

        # preparations by user like creating PeriodicalCallbacks
        self.custom_preparation()

        # device_names = [d.name for d in self._devices]
        self.info = self.get_image()

        # the loop
        self.loop = IOLoop.current()
        self.logger("go to loop")
        self.ping_timer.start()
        self._status = "work"
        # go to endless loop with reading messages and checking PeriodicalCallbacks, created by user
        self.loop.start()

    def get_image(self):
        """ creates info dict for this node """
        # self.logger("devices : {}".format(self._devices))
        device_images = {d.name: d.get_image() for d in self._devices}
        # self.logger("device images: {}".format(device_images))
        # custom_command_images = {d.name: d.get_image() for d in self.custom_commands}
        # self.logger("custom_command_images: {}".format(custom_command_images))


        # also lets add node`s itself methods, those can be requested by
        # setting device name same as node name

        system_command_images = {c.name: c.get_image() for c in self.system_commands}
        # self.logger("system_command_images: {}".format(system_command_images))

        image_ = {
            "name": self.name,
            "annotation": self._annotation,
            "status": self._status,
            "devices": device_images,
            "system_commands": system_command_images  #,
            # "custom_commands": custom_command_images
        }
        return image_

    def send(self, stream: ZMQStream, msg_to_send: Message):
        """handler for sending data to another node through local broker """
        # prepare msg
        msg = msg_to_send.create_zmq_msg()
        # then put its id to queue
        # self.store_awaiting_msg(msg_to_send)

        # also lets save last sent msg time in network config
        self.network_state[msg_to_send.addr]["last_msg_sent"] = time.time()
        self.logger("self network state: {}".format(self.network_state))

        # self.logger("msg to {} is {}".format(msg_to_send.addr, msg))
        # send msg
        stream.send_multipart(msg)

    def reqv_callback(self, stream: ZMQStream, reqv_msg: list):
        """base callback for all messages in all streams"""
        self.logger("reqv callback")
        self.logger("we got msg: {}".format(reqv_msg))
        # parse
        addr_decoded, decoded_dict = Message.parse_zmq_msg(reqv_msg)
        # self.logger([addr_decoded, decoded_dict])
        decoded_msg = Message.create_msg_from_addr_and_dict(addr_decoded=addr_decoded, decoded_dict=decoded_dict)
        self.logger(decoded_dict)

        # msg_id = msg_dict["id"]
        # command = msg_dict["command"]
        # device_name = msg_dict["device"]  # that is a str with device name
        # msg_data = msg_dict["data"]
        # msg_time = msg_dict["time"]

        # lets check if that node in our noeds list:
        if addr_decoded in self.network_state.keys():
            self.network_state[addr_decoded]["last_msg_received"] = time.time()
            self.logger("self network state: {}".format(self.network_state))
        else:
            self.logger("found new node by irs reqv: {}".format(addr_decoded))
            self.logger("we will add it to our network state container")
            # TODO mb it is good to add unknown node to our ping list?
            self.network_state[addr_decoded] = {"address": "unknown",
                                                # todo how to find addr? in form "tcp://192.168.100.8:5568"
                                                               "status": "unknown",
                                                               "last_msg_sent": None,
                                                               "last_msg_received": time.time()}

            self.logger("self network state: {}".format(self.network_state))

        # 1) lets check if it is response for one of our requests to another node
        self.logger(decoded_dict["command"])

        if decoded_dict["command"] == "resp":
            # so we dont care about "device" field
            # it means that it it resp to us and we must not answer
            # answered_resp = self.extract_awaiting_msg(decoded_dict["msg_id"])
            self.logger("command resp received in msg with id {}".format(decoded_dict["msg_id"]))
            self.logger("msg body is {}".format(decoded_dict))

            # here app must find original msg by its id and delete it from unanswered queue
            # also if it was resp for some system call, it must be handled here, before user parsing
            # print(stream, decoded_msg)
            self.system_resp_handler(stream=stream, resp_msg=decoded_msg)
            # and there - user parsing
            self.custom_response_parser(stream=stream, resp_msg=decoded_msg)

        # there is a list of system commands that we use under the hood
        # 2) check if it is command to node
        elif decoded_dict["device"] == self.name:
            # it means that msg was sent directly to node
            self.handle_system_msgs(stream, decoded_msg)

        # 3) check if it is command to one of our devices
        # let's check which device the message was sent to

        else:
            found_flag = False
            for device_ in self._devices:
                self.logger("msg device is {}".format(decoded_dict["device"]))
                if device_.name == decoded_dict["device"]:
                    found_flag = True
                    self.logger("found requested device in our devices {}".format(device_.name))
                    # then call selected method on this device with that params
                    try:
                        if decoded_dict["data"]:  # because it can be empty or b'' or None or smth same
                            result = device_.call(decoded_dict["command"], **decoded_dict["data"])
                        else:
                            result = device_.call(decoded_dict["command"], **{})
                        # encoded_result = pickle.dumps(result)
                        res_msg = Message(
                            addr=addr_decoded,
                            device=decoded_dict["device"],
                            command="resp",
                            msg_id=decoded_dict["msg_id"],
                            time_=time.time(),
                            data=result
                        )
                        self.logger("try to send resp {}".format(res_msg))
                        self.send(stream, res_msg)
                    except Exception as e:
                        error_str = "error while calling device: {}".format(e)
                        self.logger(error_str)
                        res_msg = Message(
                            addr=addr_decoded,
                            device=decoded_dict["device"],
                            command="resp",
                            msg_id=decoded_dict["msg_id"],
                            time_=time.time(),
                            data=error_str
                        )
                        self.logger("try to send resp with error {}".format(res_msg))
                        self.send(stream, res_msg)

            # this is shit and we dont want to handle it
            if not found_flag:
                self.logger("command {} is not system, trying to use user handler".format(decoded_dict["command"]))
                # 5) may be user want to handle it somehow
                self.custom_request_parser(stream, decoded_msg)

    def handle_system_msgs(self, stream, reqv_msg: Message):
        """handler to base commands, those can be sent to every node by another node"""
        if reqv_msg.command == "info":
            # it means that it it reqv to us and we must answer
            # in answer we need to send all info about node and its devices
            self.logger("command info received")
            self.info = self.get_image()

            res_msg = Message(
                addr=reqv_msg.addr,
                device=reqv_msg.device,
                command="resp",
                msg_id=reqv_msg.msg_id,
                time_=time.time(),
                data=self.info
            )
            self.send(stream, res_msg)

        elif reqv_msg.command == "ping":
            # it means that it it reqv to us and we must answer
            # in answer we need to send all info about node and its devices
            self.logger("command ping received")
            res_msg = Message(
                addr=reqv_msg.addr,
                device=reqv_msg.device,
                command="resp",
                msg_id=reqv_msg.msg_id,
                time_=time.time(),
                data="ack"  # TODO add here full network map to use in hot_plug situation
            )
            self.send(stream, res_msg)
            # we have to send resp with standard info about this node and its devices

        elif reqv_msg.command == "kill":
            # it means that it it reqv to us and we must answer
            # in answer we need to send all info about node and its devices
            self.logger("command ping received")
            res_msg = Message(
                addr=reqv_msg.addr,
                device=reqv_msg.device,
                command="resp",
                msg_id=reqv_msg.msg_id,
                time_=time.time(),
                data="ack"
            )
            self.send(stream, res_msg)
            # then kill itself
            self.suicide()

        else:
            self.handle_custom_system_msgs(stream, reqv_msg)

    def suicide(self):
        """ command to kill node """
        # self.loop.stop()
        self.logger("{} will be killed right now".format(self.name))
        self.ping_timer.stop()
        # while self.ping_timer.is_running():
        #     time.sleep(0.1)
        self.logger("ping timer is running: {}".format(self.ping_timer.is_running()))
        self.loop.stop()
        self.loop.close()  # TODO fix or simply catch exception

    def handle_custom_system_msgs(self, stream, reqv_msg: Message):
        """ user can handle here any custom commands for his custom node"""
        pass

    def on_ping_timer(self):
        # method to ping other sockets
        # self.logger("try to send ping")
        for s in self._sockets.keys():

            ping_msg = Message(
                addr=s,
                device=s,  # here addr is name and device is name too
                command="ping",
                msg_id=uuid.uuid4().hex,
                time_=time.time(),
                data=b''
            )
            self.send(stream=self._sockets[s]["stream"], msg_to_send=ping_msg)

    # def store_awaiting_msg(self, resp_msg: Message):
    #     """ user can override this method if needs"""
    #     # TODO

    # def extract_awaiting_msg(self, resp_msg: Message):
    #     """ user can override this method if needs"""
    #     # TODO
    #     msg = Message.create_msg_from_addr_and_dict("pass", dict())
    #     return msg

    def system_resp_handler(self, stream: ZMQStream, resp_msg: Message):
        """ user can override this method if needs"""
        # TODO
        pass



if __name__ == "__main__":
    pass