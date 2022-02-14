import os.path
import sys
# here we trying to manually add our lib path to python path
abspath = os.path.abspath("../..")
# print(abspath)
sys.path.insert(0, "{}/low_level_drivers".format(abspath))
# print(sys.path)

from virtual_serial_device import SerialEmulator
from random import uniform
from time import sleep



emulator = SerialEmulator('./ttydevice','./ttyclient')
while(True):
    emulator.write('foo: {:.2f}\n'.format(uniform(10, 20)).encode())
    sleep(1)
