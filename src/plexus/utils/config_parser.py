"""
simple config parser handler
"""
import time, sys, os
import treelib


# example:
#
# exp_config = {
#     "experiment": "test1",
#     "addresses":
#         {
#             "pc1": "tcp://192.168.100.4:5566",
#             "pc2": "tcp://192.168.100.8:5566"
#         }
#         # pc_name : tcp addr and port
#         # every broker must know own pc name
# }

class ConfigParser():
    """

    """
    # __slots__ = ()

    def __init__(self):
        # super().__init__()
        self.config = None
        pass

    def init_from_dict(self,  exp_config):

        self.config = exp_config

        self.exp_tree = treelib.Tree()
        self.exp_tree.create_node("{} - {}".format("experiment", self.config["experiment"]), 1)
        counter = 1
        last_counter = counter
        for broker in self.config["brokers"]:
            print(broker)
            counter = counter + 1
            self.exp_tree.create_node("{} - {}".format(
                broker, self.config["brokers"][broker]), counter, parent=1)
            last_counter = counter
            for node in self.config["brokers"][broker]["nodes"]:
                counter = counter + 1
                self.exp_tree.create_node("{} - {}".format(
                    node,
                    self.config["brokers"][broker]["nodes"][node]), counter, parent=last_counter)

    def init_from_yaml(self, path):
        pass  # todo

    def get_brokers(self):
        return self.config["brokers"]

    def get_nodes(self, broker):
        return self.config["brokers"][broker]["nodes"]

    def get_devices(self, broker, node):
        return self.config["brokers"][broker]["nodes"][node]

    def get_exp_info(self):
        return self.config["experiment"]

    def show_pretty_graph(self):
        self.exp_tree.show()


# https://stackoverflow.com/questions/4014621/a-python-class-that-acts-like-dict
# https://stackoverflow.com/questions/682504/what-is-a-clean-pythonic-way-to-have-multiple-constructors-in-python
# TODO


if __name__ == "__main__":
    # example:

    c = ConfigParser()

    exp_config = {
        "experiment": "test1",
        "description": "nice test experiment",
        "brokers":
        {
            "pc1": {
                "addr": "tcp://192.168.100.4:5566", "nodes":
                {
                    "node1": {"description": "temp", "devices": {}},
                    "node2": {"description": "temp", "devices": {}},
                    "node3": {"description": "temp", "devices": {}},
                 },
            },
            "pc2": {
                "addr": "tcp://192.168.100.8:5566", "nodes":
                {
                    "node6": {"description": "temp", "devices": {}},
                    "node4": {"description": "temp", "devices": {}},
                    "node5": {"description": "temp", "devices": {}},
                },
            }
        }
    }
    print(exp_config["brokers"]["pc1"]["addr"])
    c.init_from_dict(exp_config)
    # c = ConfigParser(exp_config)
    print(c.get_brokers())
    print(c.get_nodes("pc1"))
    c.show_pretty_graph()

