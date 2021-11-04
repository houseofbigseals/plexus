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

class ConfigParser(dict):
    """

    """
    # __slots__ = ()

    def __init__(self):
        super().__init__()
        self.config = None
        pass

    def init_from_dict(self,  exp_config):

        self.config = exp_config

        self.exp_tree = treelib.Tree()
        self.exp_tree.create_node("{} - {}".format("experiment", self.config["experiment"]), 1)
        counter = 1
        for addr in self.config["addresses"]:
            counter = counter + 1
            self.exp_tree.create_node("{} - {}".format(addr, self.config["addresses"][addr]), counter, parent=1)

    def init_from_yaml(self, path):
        pass  # todo

    def get_machines(self):
        return self.config["addresses"]

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
        "addresses":
            {
                "pc1": "tcp://192.168.100.4:5566",
                "pc2": "tcp://192.168.100.8:5566"
            }
        # pc_name : tcp addr and port
        # every broker must know own pc name
    }
    c.init_from_dict(exp_config)
    # c = ConfigParser(exp_config)
    c.show_pretty_graph()

