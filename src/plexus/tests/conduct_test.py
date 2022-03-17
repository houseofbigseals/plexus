#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import serial
import time
import sys



# custom path imports
try:
    from plexus.nodes.node import BaseNode, PeriodicCallback
    from plexus.nodes.message import Message
    from plexus.nodes.command import Command
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

    # first data
    u_s = np.array([0.005, 2.048, 2.597, 3.092, 3.336, 3.480, 3.602])
    e_s = np.array([0.007, 0.519, 0.801, 1.372, 1.973, 2.524, 3.114])

    # # second data
    # u_s = np.array([])
    # e_s = np.array([])

    # f = plt.figure()
    def exp_func(tt, a, b):
        return a * np.exp(b * tt)

    def squad_func(t, a, b, c):
        return a*t*t + b*t + c

    def triad_func(t, a, b, c, d):
        return a*t*t*t + b*t*t + c*t + d

    def quad_func(t, a, b, c, d, e):
        return a*t*t*t*t + b*t*t*t + c*t*t + d*t + e

    def fffffunc(t, a, b):
        return a*t/(b-t)

    epopt, er2 = approximation_with_r2(exp_func, u_s, e_s)
    spopt, sr2 = approximation_with_r2(squad_func, u_s, e_s)
    tpopt, tr2 = approximation_with_r2(triad_func, u_s, e_s)
    qpopt, qr2 = approximation_with_r2(quad_func, u_s, e_s)
    # fpopt, fr2 = approximation_with_r2(fffffunc, u_s, e_s)


    print("exp approx: coeffs = {} r2 = {}".format(epopt, er2))
    print("squad approx: coeffs = {} r2 = {}".format(spopt, sr2))
    print("triad approx: coeffs = {} r2 = {}".format(tpopt, tr2))
    print("quad approx: coeffs = {} r2 = {}".format(qpopt, qr2))
    # print("hyperbola approx: coeffs = {} r2 = {}".format(fpopt, fr2))

    x = np.arange(0, 3.75, 0.1)
    y_eopt = exp_func(x, *epopt)
    y_spopt = squad_func(x, *spopt)
    y_tpopt = triad_func(x, *tpopt)
    y_qpopt = quad_func(x, *qpopt)
    y_fpopt = fffffunc(x, *[0.4819, 4.1594])

    residuals = e_s - fffffunc(u_s, 0.4819, 4.1594)
    residuals2 = e_s - exp_func(u_s, *epopt)
    print(residuals)
    print(residuals2)
    ss_res = np.sum(residuals ** 2)
    ss_tot = np.sum((e_s - np.mean(e_s)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)


    plt.plot(x, y_eopt, '-b')
    plt.plot(x, y_spopt, '-g')
    plt.plot(x, y_tpopt, '-c')
    plt.plot(x, y_qpopt, '--r')
    plt.plot(x, y_fpopt, '-.k')
    plt.plot(u_s, e_s, 'or')

    plt.xlabel('U, volts, internal sensor')
    plt.ylabel('E, mSm, external sensor')
    legend1 = "{:.3f}*exp({:.3f}*x), R2 = {:.2f}".format(*epopt, er2)
    legend2 = "{:.3f}*x2 + {:.3f}*x + {:.3f}, R2 = {:.2f}".format(*spopt, sr2)
    legend3 = "{:.3f}*x3 + {:.3f}*x2 + {:.3f}*x + {:.3f}, R2 = {:.2f}".format(*tpopt, tr2)
    legend4 = "{:.3f}*x4 + {:.3f}*x3 + {:.3f}*x2 + {:.3f}*x + {:.3f}, R2 = {:.2f}".format(*qpopt, qr2)
    legend5 = "{:.3f}*x / ({:.3f} - x), R2 = {:.2f}".format(0.4819021, 4.159421, r_squared)
    plt.legend([legend1, legend2, legend3, legend4, legend5, "Raw data"], loc="upper left")
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

        # additional system command
        one_cycle_command = Command(
            name="one_cycle",
            annotation="one cycle of measurement on conduct stand",
            output_kwargs={"ack_msg": "ok"}
        )

        status_command = Command(
            name="exp_status",
            annotation="returns short info about experiment status",
            output_kwargs={"status_string": "status"}
        )
        self._annotation = "control node for conductivity control stand with mixer"
        self._devices.extend([self.avr_cond_dev, self.avr_relay_dev])

        self.system_commands.append(one_cycle_command)
        self.system_commands.append(status_command)

        self.logger("my system commands")
        self.logger(self.system_commands)

        self.need_one_cycle = False
        # self.num_of_done_cycles = 0
        # self.max_num_of_cycles = 10
        self.measure_pause = 5000  # ms
        self.time_quant = 10  # ms
        self.sleep_timer_delay = 0  # ms
        self.system_stage_flag = "waiting for the start of cycle"

        # channels on real device
        self.mixing_pump = 1
        self.output_valve = 2
        self.dosing_pump = 3
        self.input_pump = 4

        # exp data storaging

    def custom_preparation(self):
        self.logger("custom init")
        # self.system_stage_flag = "waiting for the start of cycle"
        self.system_timer = PeriodicCallback(self.on_system_timer, self.time_quant)  # ms
        self.system_timer = PeriodicCallback(self.on_data_saving, self.measure_pause)  # ms
        self.system_timer.start()
        self.logger("start work")

    # def convert_u_to_e(self, u_volts):
    #     pass

    def on_data_saving(self):
        conductivity = self.avr_cond_dev.call("get_approx_data")
        self.logger(conductivity)

    def on_system_timer(self):

        if self.sleep_timer_delay > 0:
            # it means that we have to wait some more time
            # lets decrease global delay timer
            self.sleep_timer_delay = self.sleep_timer_delay - self.time_quant

        else:
            if self.system_stage_flag == "need_dozing":
                # it means that we have to work
                self.avr_relay_dev.call(command="on", input_kwargs={"channel": self.dosing_pump})
                self.system_stage_flag = "need_mixing"
                self.sleep_timer_delay = 3000
            elif self.system_stage_flag == "need_mixing":
                self.avr_relay_dev.call(command="off", input_kwargs={"channel": self.dosing_pump})
                self.avr_relay_dev.call(command="on", input_kwargs={"channel": self.mixing_pump})
                self.system_stage_flag = "need_draining"
                self.sleep_timer_delay = 480000
            elif self.system_stage_flag == "need_draining":
                self.avr_relay_dev.call(command="off", input_kwargs={"channel": self.mixing_pump})
                # here must be code for draining 40 ml of water out from system
                self.system_stage_flag = "waiting for the start of cycle"

    def handle_custom_system_msgs(self, stream, reqv_msg: Message):
        addr_decoded, decoded_dict = Message.parse_zmq_msg(reqv_msg)
        # self.logger([addr_decoded, decoded_dict])
        # decoded_msg = Message.create_msg_from_addr_and_dict(addr_decoded=addr_decoded, decoded_dict=decoded_dict)
        self.logger(decoded_dict)
        if decoded_dict["command"] == "one_cycle":
            self.system_stage_flag = "need_dozing"
            res_msg = Message(
                addr=addr_decoded,
                device=decoded_dict["device"],
                command="resp",
                msg_id=decoded_dict["msg_id"],
                time_=time.time(),
                data="ok"
            )
            return res_msg

        if decoded_dict["command"] == "status":
            res_msg = Message(
                addr=addr_decoded,
                device=decoded_dict["device"],
                command="resp",
                msg_id=decoded_dict["msg_id"],
                time_=time.time(),
                data=self.system_stage_flag
            )
            return res_msg




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

