import uuid
import time
import pickle
from typing import Any

"""
for now msg is list 
[
from_addr: bytes, -ascii encoded name_str of sender node
b'', - empty byte delimiter
msg_dict: bytes - serialized by pickle dict with all information
]

msg_dict:
{addr: str, device: str, command: str, msg_id: str - created by uuid4().hex, data: Any}

you can send any type of data in data field, but in most cases 
it is dict with correspond arguments for command
"""


class Message:
    """
    Wrapper for user-friendly message constructing
    and for hiding all shit that are inside
    needs addr, command, deice and args
    returns zmq-compatible message
    """
    def __init__(self,
                 addr: str,
                 device: str,
                 command: str,
                 msg_id: str = None,
                 data: Any = None,
                 time_: float = None
                 ):
        """

        """
        self.addr = addr
        self.device = device
        self.command = command
        self.msg_id = msg_id if msg_id else uuid.uuid4().hex
        self.data = data if data else b''
        self.time = time_ if time_ else time.time()

        # create dict
        self.msg_dict = dict()
        self.msg_dict["device"] = self.device
        self.msg_dict["command"] = self.command
        self.msg_dict["msg_id"] = self.msg_id
        self.msg_dict["time"] = self.time
        self.msg_dict["data"] = self.data

        # create encoded msg, ready to send
        self.msg_encoded = [self.addr.encode('ascii'), b'', pickle.dumps(self.msg_dict)]

    def create_zmq_msg(self):
        return self.msg_encoded

    @classmethod
    def parse_zmq_msg(cls, msg):
        addr_decoded = msg[0].decode('ascii')
        decoded_dict = pickle.loads(msg[2])
        return addr_decoded, decoded_dict

    @classmethod
    def create_msg_from_addr_and_dict(cls, addr_decoded: str, decoded_dict: dict):
        new_msg = Message(
            addr=addr_decoded,
            device=decoded_dict["device"],
            command=decoded_dict["command"],
            msg_id=decoded_dict["msg_id"],
            data=decoded_dict["data"],
            time_=decoded_dict["time"]
        )
        return new_msg

