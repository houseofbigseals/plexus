
import subprocess
import time, sys, os
try:
    from devices.base_device import BaseDevice
    from low_level_drivers.bmp180_driver import get_bmp180_data
except ModuleNotFoundError:
    # here we trying to manually add our lib path to python path
    abspath = os.path.abspath("..")
    sys.path.insert(0, "{}/devices".format(abspath))
    sys.path.insert(0, "{}/low_level_drivers".format(abspath))
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
        self._available_commands.extend(["get_state", "get_temperature",
                                         "get_pressure", "get_temp_and_press"])

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
