
from abc import ABC, abstractmethod
from plexus.nodes.command import Command
from plexus.utils.logger import PrintLogger


class BaseDevice(ABC):
    """

    """
    # abstract method, that must be overridden in the child class
    @abstractmethod
    def device_commands_handler(self, command, **kwargs):
        """
        here developer can add handling of its own commands

        # WARNING: must be redefined by user even if it is empty - then fill it with 'pass' !

        :param command:
        :param kwargs:
        :return:

        available_states:
        "not_started",  # device is ok, but it is still not started by user
        "paused",  # device is ok, but user paused it manually
        "finished",  # device is ok and it was successfully finished by user
        "works",  # device at work, all things goes ok
        "warning",  # small error, but you have to know about it
        "error",  # big error, but device still can work somehow
        "critical"  # fatal error, device is dead

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
        self._available_commands = []

        info_command = Command(
            name="info",
            annotation="full info about device and its commands",
            output_kwargs={"info_str": "str"},
            action=self.get_image
        )

        self.add_command(info_command)

        # if user needs that commands, he has to write them by himself

        # start_command = Command(
        #     name="start",
        #     annotation="command to do some mystical preparation work like low-level calibration",
        #     output_kwargs={"ack_str": "str"}
        #
        # )
        #
        # stop_command = Command(
        #     name="stop",
        #     annotation="command to do some mystical pausing work like closing valves or smth",
        #     output_kwargs={"ack_str": "str"}
        # )
        #
        # kill_command = Command(
        #     name="kill",
        #     annotation="command to fully stop work of device",
        #     output_kwargs={"ack_str": "str"}
        # )


        # user have to manually add his custom commands to that list by add_command() function

        self._image = self.get_image()

    def add_command(self, command):
        """simple wrapper for looking serious """
        self._available_commands.extend([command])

    def get_image(self):
        """ get string representation of device for user information """
        command_images = {c.name: c.get_image() for c in self._available_commands}
        image_ = {
            "name": self.name,
            "annotation": self._annotation,
            "status": self._status,
            "commands": command_images
        }
        return image_

    def __call__(self, command, **kwargs):
        """simply execute method with name = 'command' and args = **kwargs"""
        if command == "info":
            return self.get_image()
        else:
            command_found = False
            for com in self._available_commands:
                if com.name == command and not command_found:
                    command_found = True
                    try:
                        return str(com(**kwargs))  # is it good?
                    except Exception as e:
                        return str(e)   # is it good?

            if not command_found:
                # must be redefined by user even if it is empty - then fill it with 'pass'
                return self.device_commands_handler(command, **kwargs)

    def __setattr__(self, key, value):
        # do we even need that list of states? mb remove them
        # Set of available states must not be changed
        if key == '_available_states' and hasattr(self, '_available_states'):
            raise AttributeError('Set of available states cannot be changed')
        else:
            self.__dict__[key] = value



if __name__ == "__main__":
    pass
