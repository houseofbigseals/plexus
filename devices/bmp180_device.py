
import subprocess
import time, sys, os
try:
    from devices.base_device import BaseDevice
    from low_level_drivers.bmp180_driver import get_bmp180_data
    from nodes.command import Command
except ModuleNotFoundError:
    # here we trying to manually add our lib path to python path
    abspath = os.path.abspath("..")
    sys.path.insert(0, "{}/devices".format(abspath))
    sys.path.insert(0, "{}/low_level_drivers".format(abspath))
    sys.path.insert(0, "{}/nodes".format(abspath))
    from command import Command
    from base_device import BaseDevice
    from bmp180_driver import get_bmp180_data


class BMP180Sensor(BaseDevice):
    """

    """
    def __init__(self, name):
        super().__init__(name)
        # manually add here important variables and commands
        self.bmp_180_state = "None"
        self._description = "this is simple test device to control simple sensor"

        get_state_command = Command(
            name="get_state",
            annotation="get_state of sensor",
            output_kwargs={"state": "str"}
        )

        get_temperature_command = Command(
            name="get_temperature",
            annotation="get_temperature",
            output_kwargs={"temp": "float"}
        )

        get_pressure_command = Command(
            name="get_pressure",
            annotation="get_pressure",
            output_kwargs={"pressure": "float"}
        )

        get_temp_and_press_command = Command(
            name="get_temp_and_press",
            annotation="get_temp_and_press",
            output_kwargs={"temp and pressure": "tuple"}
        )


        self._available_commands.extend([get_pressure_command, get_temperature_command,
                                         get_temp_and_press_command, get_state_command])

    def device_commands_handler(self, command, **kwargs):
        if command == "get_state":
            print("command == 'get_state'")
            # do kill program: blink 5 times in 1 secs
            return self._status
        if command == "get_temperature":
            try:
                temp, pressure, altitude = get_bmp180_data()
                self._status = "works"
                return temp
            except Exception as e:
                self._status = "error"
                return e
        if command == "get_pressure":
            try:
                temp, pressure, altitude = get_bmp180_data()
                self._status = "works"
                return pressure
            except Exception as e:
                self._status = "error"
                return e

        if command == "get_temp_and_press":
            try:
                temp, pressure, altitude = get_bmp180_data()
                self._status = "works"
                return temp, pressure
            except Exception as e:
                self._status = "error"
                return e


if __name__ == "__main__":
    c = BMP180Sensor("bmp1")
    print(c.call("info"))
    print(c.call("get_state"))
    while True:
        print(c.call("get_temperature"))
        time.sleep(1)
        print(c.call("get_temp_and_press"))
        time.sleep(1)
    # c.call("start")
