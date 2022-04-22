

import time, sys, os
try:
    from devices.base_device import BaseDevice
    from low_level_drivers.si7021_driver import get_si7021_data
    from src.plexus.nodes import Command
except ModuleNotFoundError:
    # here we trying to manually add our lib path to python path

    from plexus.nodes.command import Command
    from plexus.devices.base_device import BaseDevice
    from plexus.low_level_drivers.si7021_driver import get_si7021_data


class SI7021(BaseDevice):
    """

    """
    def __init__(self, name):
        super().__init__(name)
        # manually add here important variables and commands
        # self.si7021_state = "None"
        self._description = " SI7021 temp and humidity handler device "

        get_state_command = Command(
            name="get_state",
            annotation="get_state of sensor",
            output_kwargs={"state": "str"}
        )

        get_temp_and_hum_command = Command(
            name="get_temp_and_hum",
            annotation="get temp and hum data",
            output_kwargs={"temp and pressure": "tuple"}
        )

        get_hum_command = Command(
            name="get_hum",
            annotation="get hum data",
            output_kwargs={"hum": "float"}
        )

        get_temp_command = Command(
            name="get_temp",
            annotation="get temp data",
            output_kwargs={"temp": "float"}
        )

        self._available_commands.extend([get_temp_and_hum_command, get_hum_command,
                                         get_temp_command, get_state_command])

    def device_commands_handler(self, command, **kwargs):
        if command == "get_state":
            print("command == '{}'".format(command))
            return self._status

        if command == "get_temp":
            print("command == '{}'".format(command))
            try:
                cels_temp, humidity = get_si7021_data()
                self._status = "works"
                return cels_temp
            except Exception as e:
                self._status = "error"
                return e

        if command == "get_hum":
            print("command == '{}'".format(command))
            try:
                cels_temp, humidity = get_si7021_data()
                self._status = "works"
                return humidity
            except Exception as e:
                self._status = "error"
                return e

        if command == "get_temp_and_hum":
            try:
                print("command == '{}'".format(command))
                cels_temp, humidity = get_si7021_data()
                self._status = "works"
                return cels_temp, humidity
            except Exception as e:
                self._status = "error"
                return e

if __name__ == "__main__":
    c = SI7021("si7021")
    print(c.call("info"))
    print(c.call("get_state"))
    while True:
        print(c.call("get_temp"))
        time.sleep(1)
        print(c.call("get_hum"))
        time.sleep(1)
        print(c.call("get_state"))
        time.sleep(1)