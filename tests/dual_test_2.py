
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
    client = PlexusUserApi(endpoint="tcp://10.9.0.1:5565", name="client", list_of_nodes=list_of_nodes1)
    # client = PlexusUserApi(endpoint="tcp://10.9.0.21:5565", name="client", list_of_nodes=list_of_nodes1)

    while True:
        # 1
        print("\nhi\navailable nodes are:")
        for n in list_of_nodes1:
            print(n)

        user_node = input("select node: ")
        print("your input: {}".format(user_node))

        # now we have to get info about this node to show it to user
        info_message = Message(
            addr=str(user_node),
            device=str(user_node),
            command="info",
            msg_id=uuid.uuid4().hex,
            time_=time.time()
        )

        print("msg to send is {}".format(info_message))
        res = client.send_msg(info_message)
        # print("we got raw resp: {}".format(res))
        addr_decoded, decoded_resp = Message.parse_zmq_msg(res)
        print("=================================================================")
        print("we got resp from node: {}".format(user_node))
        for i in decoded_resp:
            print(i, type(i))
        all_answer = decoded_resp["data"]

        print("{} - {}".format("device", decoded_resp["device"]))
        print("{} - {}".format("command", decoded_resp["command"]))

        print("=================================================================")

        for dev in decoded_resp["data"]["devices"]:
            # print("{} - {}\n".format(dev, all_answer[key]))
            print("======== device name - {}".format(all_answer["devices"][dev]["name"]))
            print("======== device state - {}".format(all_answer["devices"][dev]["status"]))
            print("======== device info - {}".format(all_answer["devices"][dev]["info"]))


            print("=================================================================")

            for comm in decoded_resp["data"]["devices"][dev]["commands"]:
                print("================ {} - {}".format(comm, decoded_resp["data"]["devices"][dev]["commands"][comm]))
        #2

        print("available devices for that node:")
        for dev in decoded_resp["data"]["devices"]:
            print("======== device name - {}".format(decoded_resp["data"]["devices"][dev]["name"]))
        user_device = input("select device: ")
        print("your input: {}".format(user_device))
        if user_device == user_node:

        #3
        print("available commands for that device:")
        for comm in decoded_resp["data"]["devices"][user_device]["commands"]:
            print("================ {} - {}".format(comm, decoded_resp["data"]\
            ["devices"][user_device]["commands"][comm]))
        user_command = input("select command: ")
        print("your input: {}".format(user_command))


        #4
        print("available args for that device: ")
        # for arg_ in decoded_resp["data"]["devices"][user_device]["commands"][user_command]["input_kwargs"]:
        print("========================= {} ".format(
                decoded_resp["data"]["devices"][user_device]["commands"][user_command]["input_kwargs"]
        ))
        user_args = dict()
        if decoded_resp["data"]["devices"][user_device]\
            ["commands"][user_command]["input_kwargs"]:
            for a in decoded_resp["data"]["devices"][user_device]\
                ["commands"][user_command]["input_kwargs"].keys():
                user_args[a] = input("write arg {} : ".format(a))


        # user_args = input("write args in string like in previous template: ")
        # here must be also parsing of this string
        print("your input: {}".format(user_args))

        # TODO fix all things here

        # n2.start()
        # time.sleep(5.2)

        m = Message(
            addr=str(user_node),
            device=str(user_device),
            command=str(user_command),
            msg_id=uuid.uuid4().hex,
            time_=time.time(),
            # data={"new_state": int(user_arg)}
            data=user_args
        )


        # m = Message(
        #     addr="node1",
        #     device="numlock",
        #     command="set_state",
        #     msg_id=uuid.uuid4().hex,
        #     time_=time.time(),
        #     data={"new_state": int(user_arg)}
        # )
        #


        # m = Message(
        #     addr="node1",
        #     device="node1",
        #     command="PING",
        #     msg_id=uuid.uuid4().hex,
        #     time_=time.time(),
        #     data=b''
        # )
        print("msg to send is {}".format(m))
        res = client.send_msg(m)
        print("we got raw resp: {}".format(res))
        decoded_resp = Message.parse_zmq_msg(res)
        print("we got resp from node1:\n{}".format(decoded_resp))
