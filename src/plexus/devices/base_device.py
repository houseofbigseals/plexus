# import zmq
# import pickle
#
# from zmq.eventloop.ioloop import IOLoop, PeriodicCallback
# from zmq.eventloop.zmqstream import ZMQStream
# from multiprocessing import Process
from abc import ABC, abstractmethod

# import inspect
# from functools import wraps
# from inspect import Parameter, Signature
import sys, os

try:
    from utils.logger import PrintLogger
    from src.plexus.nodes import Command
except ModuleNotFoundError:
    # here we trying to manually add our lib path to python path
    abspath = os.path.abspath("../..")
    sys.path.insert(0, "{}/utils".format(abspath))
    sys.path.insert(0, "{}/nodes".format(abspath))
    from command import Command
    from logger import PrintLogger


class BaseDevice(ABC):
    """

    """
    # abstract methods, those must be overriden in child class
    @abstractmethod
    def device_commands_handler(self, command, **kwargs):
        """
        here developer can add handling of its own commands
        :param command:
        :param kwargs:
        :return:
        """
        pass

    # technical methods, those provide base functionality
    def __init__(self, name):
        self.name = name
        self._annotation = "Abstract BaseDevice class"  # here we can put device description
        # for more convenient work of the remote operator
        self._available_states = [
            "not_started",  # device is ok, but it is still not started by user
            "paused",  # device is ok, but user paused it manually
            "finished",  # device is ok and it was successfully finished by user
            "works",  # device at work, all things goes ok
            "warning",  # small error, but you have to know about it
            "error",  # big error, but device still can work somehow
            "critical"  # fatal error, device is dead
        ]
        self._status = "not_started"



        info_command = Command(
            name="info",
            annotation="full info about device and its commands",
            output_kwargs={"info_str": "str"}
        )

        start_command = Command(
            name="start",
            annotation="command to do some mystical preparation work like low-level calibration",
            output_kwargs={"ack_str": "str"}
        )

        stop_command = Command(
            name="stop",
            annotation="command to do some mystical pausing work like closing valves or smth",
            output_kwargs={"ack_str": "str"}
        )

        kill_command = Command(
            name="kill",
            annotation="command to fully stop work of device",
            output_kwargs={"ack_str": "str"}
        )

        self._available_commands = [info_command, stop_command, start_command, kill_command]
        # user have to manually add his custom commands to that list

        self._image = self.get_image()


        # self._available_commands = [
        #     "info",  # command for getting base description of device
        #     "start",  # command to do some mystical preparation work like low-level calibration
        #     # or simple checking that real sensor is alive
        #     "stop",  # cpmmand to do some mystical pausing work like closing valves or smth
        #     "kill"  # command to fully stop work of device
        # ]
        # also user must add here some special commands like "get_data" or "calibrate" or smth
        # and write handlers for them in device_commands_handler

    def get_image(self):



        command_images = {c.name: c.get_image() for c in self._available_commands}

        image_ = {
            "name": self.name,
            "annotation": self._annotation,
            "status": self._status,
            "commands": command_images
        }
        return image_

    def call(self, command, **kwargs):

        if command == "info":
            return self.get_image()
        else:
            # must be redefined by user
            return self.device_commands_handler(command, **kwargs)

    def __setattr__(self, key, value):
        # Set of available states must not be changed
        if key == '_available_states' and hasattr(self, '_available_states'):
            raise AttributeError('Set of available states cannot be changed')
        else:
            self.__dict__[key] = value

    # def get_image(self):
    #     """
    #     image is like a serialized footprint of object
    #     it stores all data, that user need to call this device remotely
    #     in form of dict-like object
    #     :return:
    #     """
    #     pass


# class VerySmartDevice ():
#     """
#
#     """
#     # # abstract methods, those must be overriden in child class
#     # @abstractmethod
#     # def device_commands_handler(self, command, **kwargs):
#     #     """
#     #     here developer can add handling of its own commands
#     #     :param command:
#     #     :param kwargs:
#     #     :return:
#     #     """
#     #     pass
#
#     # technical methods, those provide base functionality
#     def __init__(self, name):
#         self.name = name
#         self._description = "Abstract BaseDevice class"  # here we can put device description
#         # for more convenient work of the remote operator
#         self._available_states = [
#             "not_started",  # device is ok, but it is still not started by user
#             "paused",  # device is ok, but user paused it manually
#             "finished",  # device is ok and it was successfully finished by user
#             "works",  # device at work, all things goes ok
#             "warning",  # small error, but you have to know about it
#             "error",  # big error, but device still can work somehow
#             "critical"  # fatal error, device is dead
#         ]
#         self._status = "not_started"
#         self._available_commands = [
#             "info",  # command for getting base description of device
#             "start",  # command to do some mystical preparation work like low-level calibration
#             # or simple checking that real sensor is alive
#             "stop",  # cpmmand to do some mystical pausing work like closing valves or smth
#             "kill"  # command to fully stop work of device
#         ]
#         # also user must add here some special commands like "get_data" or "calibrate" or smth
#         # and write handlers for them in device_commands_handler
#
#     def _create_reqv(self, funcname, frame):
#
#         args = inspect.getargvalues(frame)
#         print(args)
#         print(args.args)
#         return_params = dict()
#         args.args.remove('self')
#         args.args.remove('remote')
#
#         important_params = args.args
#         raw_args = args.locals
#
#         for param in important_params:
#             return_params.update({param: raw_args[param]})
#
#         # funcname = inspect.currentframe().f_code.co_name
#         classname = type(self).__name__
#
#         return classname, funcname, return_params
#
#     def method(self,  param1: int, param2: str, remote: bool = False):
#         """
#         haha gayyyy
#         :param remote:
#         :param param1:
#         :param param2:
#         :return:
#         """
#         if not remote:
#             # do some regular work
#             return param1
#         else:
#             frame = inspect.currentframe()
#             return self._create_reqv("method", frame)
#             # it is remote call, so we need to return reqv object
#             # with info about our device, method and params, those user
#             # put here when he call us
#
#     # def call(self, command, remote=True, **kwargs):
#     #     if remote:
#     #         return self._create_reqv(self, )
#     #     if command == "info":
#     #         info = {
#     #             "name": self._name,
#     #             "info": self._description,
#     #             "status": self._status,
#     #             "commands": self._available_commands
#     #         }
#     #         return info
#     #     else:
#     #         # must be redefined by user
#     #         return self.device_commands_handler(command, **kwargs)



if __name__ == "__main__":
    pass


    # # lets prepsre node 2
    # class Node():
    #     def __init__(self):
    #         self.dev1 = VerySmartDevice("second")
    #         self.dev2 = VerySmartDevice("third")
    #         self.devices = [self.dev2, self.dev1]
    #
    #     def parse_messages(self, msg: bytes):
    #         print("node parses msgs:")
    #         name, data = pickle.loads(msg)
    #         print(data)
    #
    #         for dev in self.devices:
    #             if type(dev).__name__ == data[0] and dev.name == name:
    #                 func = getattr(dev, data[1])
    #                 result = func(**data[2])
    #                 return result
    #
    #
    #
    # # in first node
    # c = VerySmartDevice("first")
    # # local call returns result immediately
    # print(c.method(remote=False, param1=10, param2="ghj"))
    # # remote call returns smart tuple to use in another node
    # msg_data = c.method(remote=True, param1=15, param2="99999")
    # # node serializes it
    # serialized_footprint = pickle.dumps(("second", msg_data))
    # # then node1 somehow sends it to  node2
    #
    # # sending throw all brokers and networks
    #
    #
    #
    #
    #
    #
    # # node2 receives it and deserializes msg_body
    # node2 = Node()
    # print(node2.parse_messages(serialized_footprint))
    # # if we have lots of those devices with same class type,
    # # we can find the needed one by name
    # # then we have to call
    # # class_method = getattr(self, methodname)
    # #
    # # result = class_method(an_object)
    # # now it
    #

