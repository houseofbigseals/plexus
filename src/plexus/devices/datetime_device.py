import time
from pprint import pprint
from datetime import datetime
from plexus.nodes.node import Command
from plexus.devices.base_device import BaseDevice


class DatetimeDevice(BaseDevice):
    """
    this device can send you current date or time
    very useful, isn`t it?
    """

    def time_command(self, param: str):
        if param == "date":
            date = datetime.now().strftime("%Y:%m:%d")
            return date
        elif param == "time":
            timee = datetime.now().strftime("%H:%M:%S")
            return timee
        else:
            return "very big error"

    def __init__(self, name: str):
        super().__init__(name)
        self._annotation = "this device can send you current date or time,  very useful, isn`t it?"
        self._status = "started"

        time_command = Command(
            name="datetime",
            annotation="returns date or time",
            output_kwargs={"answer": "str"},
            input_kwargs={"param": "str"},
            action=self.time_command
        )
        self.add_command(time_command)

        pprint("available commands for me {}".format(self._available_commands))




if __name__ == "__main__":
    d = DatetimeDevice(
        name="fuu"
    )
    d("datetime", **{"param": "date"})
    time.sleep(2)
    d("datetime", **{"param": "time"})
    time.sleep(2)
