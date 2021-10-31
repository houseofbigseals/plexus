
import serial
import time


class VirtualDeviceHandler():
    def __init__(self, client_port='./ttyclient'):
        # self.device_port = device_port
        self.client_port = client_port
        # cmd = ['/usr/bin/socat', '-d', '-d', 'PTY,link=%s,raw,echo=0' %
        #        self.device_port, 'PTY,link=%s,raw,echo=0' % self.client_port]
        # self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1)
        self.serial = serial.Serial(self.client_port, 9600, rtscts=True, dsrdtr=True)
        self.err = ''
        self.out = ''

    def read(self):

        line = ''
        while self.serial.inWaiting() > 0:
            line += self.serial.read(1)
        last_msg = line.split("\n")[-1]
        print(last_msg)
        return last_msg

