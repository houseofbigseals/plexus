
# this is simple test device to control NumLock led state
# as if it were a some important device like relay

import subprocess
import time, sys, os
try:
    from devices.base_device import BaseDevice
    from nodes.command import Command
except ModuleNotFoundError:
    # here we trying to manually add our lib path to python path
    abspath = os.path.abspath("..")
    sys.path.insert(0, "{}/devices".format(abspath))
    sys.path.insert(0, "{}/nodes".format(abspath))
    from base_device import BaseDevice
    from command import Command


class NumLockDevice(BaseDevice):
    """

    """
    def __init__(self, name):
        super().__init__(name)
        # manually add here important variables and commands
        self.led_state = None
        self._description = "this is simple test device to control NumLock led state on Ubuntu"

        get_state_command = Command(
            name="get_state",
            annotation="get state",
            output_kwargs={"led_state": "bool"}
        )

        set_state_command = Command(
            name="set_state",
            annotation="set_state",
            output_kwargs={"ack_str": "str"}
        )

        self._available_commands.extend([set_state_command, get_state_command])

    # now we have to write handlers for start, stop and kill and other methods
    def device_commands_handler(self, command, **kwargs):
        if command == "kill":
            print("command == 'kill'")
            # do kill program: blink 5 times in 1 secs
            self.set_led(0)
            for i in range(0, 10):
                self.set_led(1)
                time.sleep(0.1)
                self.set_led(0)
                time.sleep(0.1)
            self._status = "finished"
        if command == "start":
            # check if it is alive
            print("command == 'start'")
            try:

                process = subprocess.Popen(["numlockx", "status"], stdout=subprocess.PIPE)
                output, error = process.communicate()
                self.led_state = output.decode("utf-8").split(" ")[2]
                self._status = "works"
                return "OK"
            except Exception as e:
                self._status = "critical"
                raise ConnectionError("ERROR {},\n mb try this:  'sudo apt install numlockx'".format(e))

        if command == "stop":
            print("command == 'stop'")
            # do stop program: blink 2 times in 2 secs
            self.set_led(1)
            time.sleep(0.5)
            self.set_led(0)
            time.sleep(0.5)
            self.set_led(1)
            time.sleep(0.5)
            self.set_led(0)
            time.sleep(0.5)
            self._status = "paused"

        if command == "set_state":
            print("command == 'set_state'")
            new_state = int(kwargs["new_state"])
            self.set_led(new_state)
            self._status = "works"

        if command == "get_state":
            print("command == 'get_state'")
            process = subprocess.Popen(["numlockx", "status"], stdout=subprocess.PIPE)
            output, error = process.communicate()
            # print(output, error)
            self.led_state = output.decode("utf-8").split(" ")[2].split("\n")[0]
            # print(self.led_state)
            return self.led_state

    def set_led(self, state):
        if state == 0:
            process = subprocess.Popen(["numlockx", "off"], stdout=subprocess.PIPE)
        if state == 1:
            process = subprocess.Popen(["numlockx", "on"], stdout=subprocess.PIPE)


if __name__ == "__main__":
    c = NumLockDevice("led1")
    print(c.call("info"))
    print(c.call("get_state"))
    while True:
        c.call("set_state", **{"new_state":1})
        time.sleep(1)
        c.call("set_state", **{"new_state":0})
        time.sleep(1)
    # c.call("start")
    # print(c.call("get_state"))
    # c.call("set", **{"new_state":1})
    # print(c.call("info"))
    # c.call("stop")
    # c.call("kill")
