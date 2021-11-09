
# the simpliest variant as i can imagine
from datetime import datetime
from time import sleep
from plexus.device import sensor_device, relay_device, led_device
# device is a node with predefined functionality
# like node for simple data collection from a specific sensor

from secret_config import secret_params
# for example
# secret params store all specific prams for devices and experiment
# the most important param is collective endpoint addr
# all nodes and broker must be connected to the same address
from plexus.node import UserNode, Broker, PeriodicCallback
# import user node to create own node with experiment logic

from custom_experiment_lib import diff_co2_curve, find_new_search_step, load_co2_curve_from_db, load_current_step_to_db
# custom user lib with important math and db  procedures


class GradientSearchNode(UserNode):
    # this node will be the most important in experiment
    def __init__(self, endpoint, secret_params):
        super().__init__(endpoint)
        self.main_loop_period = 15 # minutes
        self.new_light_mode = (10, 10) # default
        self.vent_time = 100
        self.measure_time = 200
        self.db_credentials = {}  # some secret db params loaded from secret config

        pass

    def user_run(self):
        # here must be preparations
        self.check_timer = PeriodicCallback(self.main_loop_check, 1000)
        self.check_timer.start()
        pass

    def main_loop_check(self):
        if datetime.now().minute % self.main_loop_period == 0 and datetime.now().second == 0:
            self.main_loop()

    def main_loop(self):
        """
        the most important function in all class :)
        :return:
        """
        # 1. get new light mode and set it
        reqv = led_device.set_light_mode(call_type="remote", red=self.new_light_mode[0], white=self.new_light_mode[1])
        # self.send("led_device_addr", "SET_LIGHT_MODE", {"red":self.new_light_mode[0], "white":self.new_light_mode[1]})
        self.send("remote_node_with_leds_addr", reqv)  # by default it must be blocking call

        # 2. start ventilation
        # open vent valves
        self.send("air_valve1", "SET", 0)
        self.send("air_valve2", "SET", 0)
        # wait them to open
        sleep(15)
        # start ventilation
        self.send("air_pump1", "SET", 0)
        self.send("air_pump2", "SET", 0)
        # wait for full ventilation time
        sleep(self.vent_time)

        # 3. calibrate co2 sensor
        self.send("co2_valve", "SET", 0)
        # send command to stop measurements
        self.send("co2_sensor", "ALLOW_MEASUREMENTS", 1)
        self.send("co2_sensor", "CALIBRATE", None)
        # wait fixed calibration time
        sleep(25)
        self.send("co2_valve", "SET", 1)
        # send command to start measurements again
        self.send("co2_sensor", "ALLOW_MEASUREMENTS", 0)

        # 4. stop ventilation
        # stop ventilation pumps
        self.send("air_pump1", "SET", 1)
        self.send("air_pump2", "SET", 1)
        # close vent valves
        self.send("air_valve1", "SET", 1)
        self.send("air_valve2", "SET", 1)
        # wait them to close
        sleep(15)

        # 5. wait for co2 measurements
        sleep(self.measure_time)

        # 6. load measured data from sql_db and calculate it
        co2_data = load_co2_curve_from_db(**self.db_credentials)
        a, b, errors = diff_co2_curve(co2_data)  # approximation as y = ax+b
        updated_search_history = load_current_step_to_db(a, **self.db_credentials)
        nred, nwhite = find_new_search_step(a, self.new_light_mode, updated_search_history)
        # if there were no problems - load new red and white params and close this search step
        self.new_light_mode = nred, nwhite

    def user_request_parser(self, from_addr, command, msg_dict):
        # here must be realized some API for user remote control of this node
        pass

    def user_response_parser(self, from_addr, command, msg_dict):
        #
        pass


if __name__ == "__main__":
    # all that nodes are independent linux processes with inter-process API
    # all communications with them we must do through Broker
    broker = Broker(**secret_params)
    broker.start()
    temp_sensor = sensor_device(**secret_params)
    temp_sensor.start()
    hum_sensor = sensor_device(**secret_params)
    hum_sensor.start()
    co2_sensor = sensor_device(**secret_params)
    co2_sensor.start()
    air_valve1 = relay_device(**secret_params)
    air_valve1.start()
    air_valve2 = relay_device(**secret_params)

