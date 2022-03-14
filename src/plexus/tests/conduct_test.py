#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import serial
import sys



# custom path imports
try:
    from plexus.nodes.node import BaseNode, PeriodicCallback
    from plexus.nodes.message import Message
    from plexus.utils.console_client import PlexusUserApi
    from plexus.devices.simple_avr_relay_device import AVRRelayDevice
    from plexus.devices.simple_avr_cond_device import AVRCondDevice
except Exception as e:
    from src.plexus.nodes.node import BaseNode, PeriodicCallback, Message
    from src.plexus.utils.console_client_api import PlexusUserApi
    from src.plexus.devices.simple_avr_relay_device import AVRRelayDevice
    from src.plexus.devices.simple_avr_cond_device import AVRCondDevice


def approximation_with_r2(func, x, y):

    import matplotlib.pyplot as plt
    from scipy.optimize import curve_fit
    import numpy as np

    popt, pcov = curve_fit(func, x, y)
    print("popt using scipy: {}".format(popt))
    print("pcov using scipy: {}".format(pcov))
    # perr = np.sqrt(np.diag(pcov))
    # print("perr using scipy: {}".format(perr))

    # to compute R2
    # https://stackoverflow.com/questions/19189362/getting-the-r-squared-value-using-curve-fit

    residuals = y - func(x, *popt)
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    print("r_squared using custom code: {}".format(r_squared))
    return popt, r_squared


def u_to_e_approximation():
    import numpy as np
    import matplotlib.pyplot as plt

    u_s = np.array([2.048, 2.597, 3.092, 3.336, 3.480, 3.602])
    e_s = np.array([0.519, 0.801, 1.372, 1.973, 2.524, 3.114])

    # f = plt.figure()
    def exp_func(tt, a, b):
        return a * np.exp(b * tt)

    def squad_func(t, a, b, c):
        return a*t*t + b*t + c

    epopt, er2 = approximation_with_r2(exp_func, u_s, e_s)
    spopt, sr2 = approximation_with_r2(squad_func, u_s, e_s)

    print("exp approx: coeffs = {} r2 = {}".format(epopt, er2))
    print("squad approx: coeffs = {} r2 = {}".format(spopt, sr2))

    x = np.arange(2, 4, 0.1)
    y_eopt = exp_func(x, *epopt)
    y_spopt = squad_func(x, *spopt)

    plt.plot(x, y_eopt, '-b')
    plt.plot(x, y_spopt, '-g')
    plt.plot(u_s, e_s, 'or')

    plt.xlabel('U, volts, internal sensor')
    plt.ylabel('E, mSm, external sensor')
    legend1 = "{:.3f}*exp({:.3f}*x), R2 = {:.2f}".format(*epopt, er2)
    legend2 = "{:.3f}*x2 + {:.3f}*x + {:.3f}, R2 = {:.2f}".format(*spopt, sr2)
    plt.legend([legend1, legend2, "Raw data"], loc="upper left")
    plt.title("Conduct sensor data approximation")

    plt.show()


class ConductStandControlNode(BaseNode):
    """

    """
    def __init__(self, endpoint: str, name: str, list_of_nodes: list, is_daemon: bool = True):
        super().__init__(endpoint, name, list_of_nodes, is_daemon)
        self.avr_relay_dev = AVRRelayDevice(
            name="avr_relay",
            num_of_channels=6,
            dev='/dev/ttyUSB0',
            baud=9600,
            timeout=1,
            slave_id=1
        )

        self.avr_cond_dev = AVRCondDevice(
            name="avr_sensor",
            dev='/dev/ttyUSB1',
            baud=9600,
            timeout=1,
            slave_id=2
        )

        self._annotation = "control node for conductivity control stand with mixer"
        self._devices.extend([self.avr_cond_dev, self.avr_relay_dev])

    def custom_preparation(self):
        self.logger("custom init")

    def convert_u_to_e(self, u_volts):
        pass


if __name__ == "__main__":
    print("we are awaiting tcp addr in format 10.9.0.1")

    # u_to_e_approximation()

    # we are awaiting addr as 10.9.0.1
    my_addr = str(sys.argv[1])

    list_of_nodes1 = [
        {"name": "node2", "address": "tcp://{}:5567".format(my_addr)}
        # {"name": "node2", "address": "tcp://10.9.0.12:5567"},
    ]
    n1 = ConductStandControlNode(name=list_of_nodes1[0]['name'], endpoint=list_of_nodes1[0]['address'],
                     list_of_nodes=list_of_nodes1)
    n1.start()
    n1.join()

