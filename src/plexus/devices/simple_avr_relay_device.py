import time


from plexus.low_level_drivers.simple_avr_relay_driver import SimpleRelayControl
from plexus.nodes.node import Command
from plexus.devices.base_device import BaseDevice


class AVRRelayDevice(BaseDevice):
    """
    this wrapper cannot really check if relay open or not
    for now it controls many relay channels, connected to AVR mcu
    """

    def on(self, channel):
        self._relay.set_relay(slave_id=self.slave_id,
                              relay_channel=channel,
                              state=0)

    def off(self, channel):
        self._relay.set_relay(slave_id=self.slave_id,
                              relay_channel=channel,
                              state=1)

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
            input_kwargs={"channel": "int"},
            action=self.on
        )
        self.add_command(on_command)

        off_command = Command(
            name="off",
            annotation="set selected channel of avr relay off",
            output_kwargs={"answer": "str"},
            input_kwargs={"channel": "int"},
            action=self.off
        )
        self.add_command(off_command)

        reboot = Command(
            name="reboot",
            annotation="reboot avr device by set DTR off and on",
            output_kwargs={"answer": "str"},
            action=self._relay.reboot
        )
        self.add_command(reboot)

        self._state = "off"
        self._status = "work"
        print("available commands for me {}".format(self._available_commands))




if __name__ == "__main__":
    d = AVRRelayDevice(
        name="fuu",
        num_of_channels=6,
        dev="/dev/ttyUSB0",
        baud=9600,
        timeout=1,
        slave_id=1
    )
    d("on", **{"channel": 1})
    time.sleep(2)
    d("off", **{"channel": 1})
    time.sleep(2)
