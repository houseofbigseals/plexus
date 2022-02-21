
try:
    from src.plexus.low_level_drivers.simple_avr_relay_driver import SimpleRelayControl
    from src.plexus.nodes.node import Command, Message
    from src.plexus.devices.base_device import BaseDevice
except Exception as e:
    from plexus.low_level_drivers.simple_avr_relay_driver import SimpleRelayControl
    from plexus.nodes.node import Command, Message
    from plexus.devices.base_device import BaseDevice


class AVRRelayDevice(BaseDevice):
    """
    this wrapper cannot really check if relay open or not
    for now it controls many relay channels, connected to AVR mcu
    """

    def __init__(self, name: str, num_of_channels: int = 6,
                 dev: str = "/dev/ttyUSB0", baud: int = 9600, timeout: int = 1, slave_id: int = 1):
        super().__init__(name)
        self._relay = SimpleRelayControl(dev=dev, baud=baud, timeout=timeout)
        self._annotation = "this is simple test device to control six relay channels through AVR mcu"
        self.slave_id = slave_id
        self.num_of_channels = num_of_channels
        self._status = "started"

        on_command = Command(
            name="on",
            annotation="set selected channel of avr relay on",
            output_kwargs={"answer": "str"},
            input_kwargs={"channel": "int"}
        )

        off_command = Command(
            name="off",
            annotation="set selected channel of avr relay off",
            output_kwargs={"answer": "str"},
            input_kwargs={"channel": "int"}
        )

        self._available_commands.extend([on_command, off_command])
        self._state = "off"
        self._status = "work"
        print("awailable commands for me {}".format(self._available_commands))

    def device_commands_handler(self, command, **kwargs):

        if command == "on":
            try:
                ch = int(kwargs["channel"])
                echo, ans = self._relay.set_relay(slave_id=1, relay_channel=ch, state=0)
                self._state = "on"
                self._status = "work"
                return ans.decode('utf-8')
            except Exception as e:
                self._status = "error"
                raise ConnectionError("ERROR {}".format(e))

        if command == "off":
            try:
                ch = int(kwargs["channel"])
                echo, ans = self._relay.set_relay(slave_id=1, relay_channel=ch, state=1)
                self._state = "off"
                self._status = "work"
                return ans.decode('utf-8')
            except Exception as e:
                self._status = "error"
                raise ConnectionError("ERROR {}".format(e))