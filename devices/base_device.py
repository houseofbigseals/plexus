import zmq
import pickle

from zmq.eventloop.ioloop import IOLoop, PeriodicCallback
from zmq.eventloop.zmqstream import ZMQStream
from multiprocessing import Process
from abc import ABC, abstractmethod, abstractproperty


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
        self._name = name
        self._description = "Abstract BaseDevice class"  # here we can put device description
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
        self._available_commands = [
            "info",  # command for getting base description of device
            "start",  # command to do some mystical preparation work like low-level calibration
            # or simple checking that real sensor is alive
            "stop",  # cpmmand to do some mystical pausing work like closing valves or smth
            "kill"  # command to fully stop work of device
        ]
        # also user must add here some special commands like "get_data" or "calibrate" or smth
        # and write handlers for them in device_commands_handler

    def call(self, command, **kwargs):
        if command == "info":
            info = {
                "name": self._name,
                "info": self._description,
                "status": self._status,
                "commands": self._available_commands
            }
            return info
        else:
            # must be redefined by user
            return self.device_commands_handler(command, **kwargs)

    def __setattr__(self, key, value):
        # Set of available states must not be changed
        if key == '_available_states' and hasattr(self, '_available_states'):
            raise AttributeError('Set of available states cannot be changed')
        else:
            self.__dict__[key] = value




if __name__ == "__main__":
    pass