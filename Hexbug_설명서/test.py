import argparse
import math

from pythonosc import dispatcher
from pythonosc import osc_server


def eeg_handler1(unused_addr, args, ch1):
    print("Blink: ", ch1)

def eeg_handler2(unused_addr, args, ch1):
    print("Jaw Clench: ", ch1)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="0.0.0.0", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=5041, help="The port to listen on")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/debug", print)
    dispatcher.map("/muse/elements/blink", eeg_handler1, "Blink")
    dispatcher.map("/muse/elements/jaw_clench", eeg_handler2, "Jaw_clench")

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()