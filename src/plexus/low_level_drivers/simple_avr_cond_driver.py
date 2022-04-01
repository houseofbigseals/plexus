import serial
import time


class SimpleCondSensorControl:
    """
            This is very simple example
            We are awaiting string like: "agbcd\n" where:
            'a' is a start byte, forever
            'g' is addr for slave device
            'd' is end byte forever
            'b' is a command
            and 'c' is nothing for that node

            so for example a130d\n is command for slave 1
            to make command 3

            answer:
            there is two answers - echo and reaction
            echo is simply received command
            reaction is
			String with value of conductivity
			or error code

			if we want to reboot arduino we have to
			https://stackoverflow.com/questions/21073086/wait-on-arduino-auto-reset-using-pyserial


    """
    def __init__(self, dev, baud, timeout):
        self.dev = dev
        self.baud = baud
        self.timeout = timeout
        self.serial_dev = serial.Serial(port=self.dev, baudrate=self.baud, timeout=self.timeout)
        print("waiting for conductivity sensor to wake up about 7 seconds")
        for i in range(7):
            time.sleep(1)
            print("wait {}".format(i))
        print("led must blink once")

    def send_command(self, com: str):
        self.serial_dev.flushInput()
        self.serial_dev.flushOutput()
        self.serial_dev.write(com.encode("utf-8"))
        flag = False
        while not flag:
            if self.serial_dev.readable():
                echo = self.serial_dev.read(7)
                ans = self.serial_dev.read(70)
                print(echo)
                print(ans)
                flag = True
        return echo, ans

    def get_data(self, slave_id: int):
        command = "a" + str(slave_id) + '1' + 'c' + "d" + "\n"
        return self.send_command(command)

    def reboot(self):
        # Toggle DTR to reset Arduino
        self.serial_dev.setDTR(False)
        time.sleep(1)
        # toss any data already received, see
        # http://pyserial.sourceforge.net/pyserial_api.html#serial.Serial.flushInput
        self.serial_dev.flushInput()
        self.serial_dev.setDTR(True)

if __name__ == "__main__":
    # c = ClotClient(
    #     dev="/dev/ttyUSB0",
    #     baud=9600,
    #     timeout=1
    # )
    # com = c.create_clot_master_command(0x01, 0x01, 0x00)
    # print(com)
    # print(c.send_command(com))
    dev = "/dev/ttyUSB1"
    baud = 9600
    timeout = 1

    c = SimpleCondSensorControl(dev, baud, timeout)
    for i in range(0, 3):
        print(c.get_data(2))

    print("now try to reload")

    c.reboot()

    for i in range(0, 3):
        print(c.get_data(2))
