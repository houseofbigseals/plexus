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
        self._sensor = SimpleCondSensorControl(dev=dev, baud=baud, timeout=timeout)
        self._annotation = "this is simple test device to control six relay channels through AVR mcu"
        self.slave_id = slave_id
        self.num_of_channels = num_of_channels
        self._status = "started"

        get_data_command = Command(
            name="get_data",
            annotation="get conductivity data from custom sensor",
            output_kwargs={"conductivity": "float"}
        )
        self._available_commands.extend([get_data_command])
        self._status = "work"
        print("awailable commands for me {}".format(self._available_commands))

    def device_commands_handler(self, command, **kwargs):

        if command == "get_data":
            try:

                echo, ans = self._sensor.get_data(self.slave_id)
                self._status = "work"
                return float(ans.decode('utf-8'))
            except Exception as e:
                self._status = "error"
                raise ConnectionError("ERROR {}".format(e))