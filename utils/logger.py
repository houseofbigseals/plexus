
from datetime import datetime

class PrintLogger():
    def __init__(self, name):
        self.name = name
        
    def __call__(self, arg):
        print("{} | {} : {}".format(datetime.now(), self.name, arg))