
from numpy import exp

try:
    from plexus.low_level_drivers.simple_avr_cond_driver import SimpleCondSensorControl
    from plexus.nodes.node import Command
    from plexus.nodes.message import Message
    from plexus.devices.base_device import BaseDevice

except Exception as e:
    from src.plexus.low_level_drivers.simple_avr_cond_driver import SimpleCondSensorControl
    from src.plexus.nodes.node import Command, Message
    from src.plexus.devices.base_device import BaseDevice


class AVRCondDevice(BaseDevice):
    """
    this wrapper for custom  connected to AVR mcu
    """

    def __init__(self, name: str, num_of_channels: int = 6,
                 dev: str = "/dev/ttyUSB1", baud: int = 9600, timeout: int = 1, slave_id: int = 2):
        super().__init__(name)

        # for ax2+bx+c approximation
        # TODO mb send it through init args?
        # self.a = 1.41433757
        # self.b = -6.43387014
        # self.c = 7.81645995
        # self.a = 1.134
        # self.b = -8.218
        # self.c = 20.264
        # self.d = -16.255
        # self.a = 0.019
        # self.b = 1.4
        self.a = 0.4819
        self.b = 4.1594  # polynomial approx
        self._sensor = SimpleCondSensorControl(dev=dev, baud=baud, timeout=timeout)
        self._annotation = "this is simple test device to control six relay channels through AVR mcu"
        self.slave_id = slave_id
        self.num_of_channels = num_of_channels
        self._status = "started"

        get_raw_data_command = Command(
            name="get_raw_data",
            annotation="get raw conductivity data from custom sensor",
            output_kwargs={"conductivity": "float"}
        )
        get_approx_data_command = Command(
            name="get_approx_data",
            annotation="get scaled conductivity data from custom sensor",
            output_kwargs={"conductivity": "float"}
        )
        self._available_commands.extend([get_raw_data_command, get_approx_data_command])
        self._status = "work"
        print("awailable commands for me {}".format(self._available_commands))

    def raw_to_approx(self, raw_data):
        x = raw_data
        # return self.a*x*x*x + self.b*x*x + self.c*x + self.d
        # return self.a*exp(self.b*x)
        return self.a*x/(self.b-x)

    def device_commands_handler(self, command, **kwargs):

        if command == "get_raw_data":
            try:
                echo, ans = self._sensor.get_data(self.slave_id)
                self._status = "work"
                return float(ans.decode('utf-8'))
            except Exception as e:
                self._status = "error"
                raise ConnectionError("ERROR {}".format(e))
        if command == "get_approx_data":
            try:
                echo, ans = self._sensor.get_data(self.slave_id)
                self._status = "work"
                rd = float(ans.decode('utf-8'))
                appr_data = self.raw_to_approx(rd)
                return appr_data
            except Exception as e:
                self._status = "error"
                raise ConnectionError("ERROR {}".format(e))