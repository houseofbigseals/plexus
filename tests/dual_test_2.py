
import time
import uuid
import sys, os

# custom path imports
try:
    from nodes.node2 import BaseNode, PeriodicCallback, Message
    from utils.console_client import PlexusUserApi
    # from nodes.broker import BrokerNode
    from devices.numlock_device import NumLockDevice
except Exception:
    # here we trying to manually add our lib path to python path
    abspath = os.path.abspath("..")
    print(abspath)
    sys.path.insert(0, "{}/nodes".format(abspath))
    sys.path.insert(0, "{}/devices".format(abspath))
    sys.path.insert(0, "{}/utils".format(abspath))
    print(sys.path)
    from node2 import BaseNode, PeriodicCallback
    from message import Message
    from console_client import PlexusUserApi
    from numlock_device import NumLockDevice


if __name__ == '__main__':

    list_of_nodes1 = [
        {"name": "node1", "address": "tcp://10.9.0.23:5566"}
        # {"name": "node1", "address": "tcp://10.9.0.23:5566"},
        # {"name": "node2", "address": "tcp://192.168.100.8:5567"},
        # {"name": "node3", "address": "tcp://192.168.100.8:5568"}
    ]


    # list_of_nodes1 = [
    #     {"name": "node1", "address": "tcp://10.9.0.21:5566"},
    #     {"name": "node2", "address": "tcp://192.168.100.8:5567"},
    #     {"name": "node3", "address": "tcp://192.168.100.8:5568"}
    # ]
    # n1 = TestLedNode(name=list_of_nodes1[0]['name'], endpoint=list_of_nodes1[0]['address'],
    #                  list_of_nodes=list_of_nodes1)
    # n2 = TestLedNode(name="node2", endpoint="tcp://192.168.100.4:5567", list_of_nodes=list_of_nodes1)
    # n3 = TestLedNode(name="node3", endpoint="tcp://192.168.100.4:5568", list_of_nodes=list_of_nodes1)
    # n1.start()
    # client = PlexusUserApi(endpoint="tcp://10.9.0.1:5565", name="client", list_of_nodes=list_of_nodes1)
    client = PlexusUserApi(endpoint="tcp://10.9.0.21:5565", name="client", list_of_nodes=list_of_nodes1)

    while True:
        user_arg = input("press new led state: ")
        print("your input: {}".format(user_arg))
        # n2.start()
        # time.sleep(5.2)

        m = Message(
            addr="node1",
            device="node1",
            command="PING",
            msg_id=uuid.uuid1(),
            time_=time.time(),
            # data={"new_state": int(user_arg)}
            data=b''
        )


        # m = Message(
        #     addr="node1",
        #     device="numlock",
        #     command="set_state",
        #     msg_id=uuid.uuid1(),
        #     time_=time.time(),
        #     data={"new_state": int(user_arg)}
        # )
        #


        # m = Message(
        #     addr="node1",
        #     device="node1",
        #     command="PING",
        #     msg_id=uuid.uuid1(),
        #     time_=time.time(),
        #     data=b''
        # )
        print("msg to send is {}".format(m))
        res = client.send_msg(m)
        decoded_resp = Message.parse_zmq_msg(res)
        print("we got resp from node1:\n{}".format(decoded_resp))
