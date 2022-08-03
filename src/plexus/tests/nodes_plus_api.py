

import pprint
from hello_world_node import HelloWorldNode
import plexus.utils.console_client_api as ccapi
from plexus.nodes.message import Message



if __name__ == "__main__":
    network = [
        # {"address": "tcp://127.0.0.1:5678"}
        {"address": "tcp://10.9.0.24:5569"}
    ]
    # n1 = HelloWorldNode(endpoint=network[0]['address'], list_of_nodes=network)
    # n1.start()

    relay_msg = Message(
    addr="tcp://10.9.0.24:5569",
    device="avr_relay",
    command="on",
    data={"channel": 3}
    )

    hello_msg = Message(
    addr="tcp://10.9.0.24:5569",
    device="tcp://10.9.0.24:5569",
    command="info"
    )

    user_api = ccapi.PlexusUserApi(
        endpoint="tcp://10.9.0.24:5679",
        list_of_nodes=network
    )

    ans = user_api.send_msg(hello_msg)
    print("ans is: {}".format(ans))
    parsed_ans = Message.print_zmq_msg(ans)
    # pp = pprint.PrettyPrinter(compact=True, width=80)

    print(parsed_ans)

    ans = user_api.send_msg(relay_msg)
    print(ans)
    parsed_ans = Message.print_zmq_msg(ans)
    print(parsed_ans)


    # pp = pprint.PrettyPrinter(compact=True, width=160)
    # for i in parsed_ans[1]["data"]:
    #     pp.pprint(i)

    # pp.pprint(parsed_ans[1]["data"])
    # n1.join()