
import plexus.utils.console_client_api as ccapi
from plexus.nodes.message import Message


if __name__ == "__main__":
    network = [
        {"address": "tcp://10.9.0.24:5569"}
    ]

    relay_msg = Message(
    addr="tcp://10.9.0.24:5569",
    device="avr_relay",
    command="off",
    data={"channel": 1}
    )

    hello_msg = Message(
    addr="tcp://10.9.0.24:5569",
    device="tcp://10.9.0.24:5569",
    command="info"
    )

    user_api = ccapi.PlexusUserApi(
        endpoint="tcp://10.9.0.24:5121",
        list_of_nodes=network
    )

    ans = user_api.send_msg(hello_msg)
    print("ans is: {}".format(ans))
    parsed_ans = Message.print_zmq_msg(ans)
    print(parsed_ans)

    ans = user_api.send_msg(relay_msg)
    print(ans)
    parsed_ans = Message.print_zmq_msg(ans)
    print(parsed_ans)
