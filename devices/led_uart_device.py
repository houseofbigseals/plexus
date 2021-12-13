
# this is simple test device to control NumLock led state
# as if it were a some important device like relay

import subprocess
import time, sys, os
try:
    from devices.base_device import BaseDevice
    from low_level_drivers.led_uart_driver import UartWrapper
    from nodes.command import Command
except ModuleNotFoundError:
    # here we trying to manually add our lib path to python path
    abspath = os.path.abspath("..")
    sys.path.insert(0, "{}/devices".format(abspath))
    sys.path.insert(0, "{}/low_level_drivers".format(abspath))
    sys.path.insert(0, "{}/nodes".format(abspath))
    from command import Command
    from base_device import BaseDevice
    from led_uart_driver import UartWrapper



class LedUartDevice(BaseDevice):
    """

    """
    def __init__(self, name: str, devname: str):
        super().__init__(name)
        # manually add here important variables and commands
        # devname must be like: "/dev/ttyUSB0"
        # or like '/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0')
        # self.led_state = None
        self._led = UartWrapper(devname)
        self._annotation = "this is simple device to control lab leds by uart"

        start_command = Command(
            name="start",
            annotation="start lightning",
            output_kwargs={"ack_str": "str"}
        )
        stop_command = Command(
            name="stop",
            annotation="stop lightning",
            output_kwargs={"ack_str": "str"}
        )

        set_red_current_command = Command(
            name="set_red_current",
            annotation="set_red_current from 10 to 250 mA",
            input_kwargs={"current": "int"},
            output_kwargs={"ack_str": "str"}
        )

        set_white_current_command = Command(
            name="set_white_current",
            annotation="set_white_current from 10 to 250 mA",
            input_kwargs={"current": "int"},
            output_kwargs={"ack_str": "str"}
        )

        get_current_command = Command(
            name="get_current",
            annotation="get last currents, saved in led driver, still undone",
            output_kwargs={"results": "tuple"}
        )


        self._available_commands.extend([start_command, stop_command, set_red_current_command ,
                                         set_white_current_command, get_current_command])
        self.red = None
        self.white = None

    # now we have to write handlers for start, stop and kill and other methods
    def device_commands_handler(self, command, **kwargs):
        if command == "stop":
            print("command == 'stop'")
            try:
                self._led.STOP()
                self._status = "finished"
                return "OK"
            except Exception as e:
                self._status = "error"
                raise ConnectionError("ERROR {}".format(e))
        if command == "start":
            # check if it is alive
            print("command == 'start'")
            try:
                self._led.START()
                self._status = "started"
                return "OK"
            except Exception as e:
                self._status = "error"
                raise ConnectionError("ERROR {}".format(e))

        if command == "set_red_current":
            print("command == 'set_red_current'")
            self.red = int(kwargs["current"])
            # self.white = int(kwargs["white"])
            try:
                self._led.START_CONFIGURE()
                self._led.SET_CURRENT(0, self.red)
                # self._led.SET_CURRENT(1, white)
                self._led.FINISH_CONFIGURE_WITH_SAVING()
                return "OK"
                # self._led.START()
            except Exception as e:
                self._status = "error"
                raise ConnectionError("ERROR {}".format(e))

        if command == "set_white_current":
            print("command == 'set_white_current'")
            self.white = int(kwargs["current"])
            # self.white = int(kwargs["white"])
            try:
                self._led.START_CONFIGURE()
                self._led.SET_CURRENT(1, self.white)
                # self._led.SET_CURRENT(1, white)
                self._led.FINISH_CONFIGURE_WITH_SAVING()
                return "OK"
                # self._led.START()
            except Exception as e:
                self._status = "error"
                raise ConnectionError("ERROR {}".format(e))

        if command == "get_current":
            print("command == 'get_current'")
            return "OK", self.red, self.white


if __name__ == "__main__":
    d = LedUartDevice(
        devname='/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0',
        name="led1"
    )
    # print(d.call("start"))
    print(d.call("stop"))
    print(d.call("set_red_current",  **{"current": 78}))
    print(d.call("set_white_current", **{"current": 79}))
    print(d.call("get_current"))
    print(d.call("start"))

