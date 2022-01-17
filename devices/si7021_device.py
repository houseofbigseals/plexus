

import time, sys, os
try:
    from devices.base_device import BaseDevice
    from low_level_drivers.si7021_driver import get_si7021_data
    from nodes.command import Command
except ModuleNotFoundError:
    # here we trying to manually add our lib path to python path
    abspath = os.path.abspath("..")
    sys.path.insert(0, "{}/devices".format(abspath))
    sys.path.insert(0, "{}/low_level_drivers".format(abspath))
    sys.path.insert(0, "{}/nodes".format(abspath))
    from command import Command
    from base_device import BaseDevice
    from si7021_driver import get_si7021_data


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
            print("command == 'get_state'")
            return self._status

        if command == "get_temp":
            try:
                cels_temp, humidity = get_si7021_data()
                self._status = "works"
                return cels_temp
            except Exception as e:
                self._status = "error"
                return e

        if command == "get_hum":
            try:
                cels_temp, humidity = get_si7021_data()
                self._status = "works"
                return humidity
            except Exception as e:
                self._status = "error"
                return e

        if command == "get_temp_and_hum":
            try:
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
        print(c.call("get_temperature"))
        time.sleep(1)
        print(c.call("get_temp_and_press"))
        time.sleep(1)
        print(c.call("get_state"))
        time.sleep(1)