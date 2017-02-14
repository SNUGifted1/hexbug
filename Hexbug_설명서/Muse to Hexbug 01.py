__author__ = 'Chanhwang Song'

import argparse
import serial 

from pythonosc import dispatcher
from pythonosc import osc_server

PORT = 'COM3'  # 아두이노 연결 포트
BAUDRATE = 9600  # 아두이노 프로그램 내의 RATE와 일치해야 함

def eeg_handler(unused_addr, args, ch1):
    global n
    n=n+1
    print("jaw clench :", ch1, n)
    
    if(n%2 == 1):
        print ("                 Go forward!")
        ser.write(b'G')
        
    else:
        print ("                    Stop!")
        ser.write(b'g')

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("--ip", default="0.0.0.0", help="The ip to listen on")

    parser.add_argument("--port", type=int, default=5041, help="The port to listen on")

    args = parser.parse_args()

  
    dispatcher = dispatcher.Dispatcher()

    dispatcher.map("/debug", print)

    dispatcher.map("/muse/elements/jaw_clench", eeg_handler, "jaw_clench")

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)

    ser = serial.Serial(PORT, BAUDRATE)

    print("Serving on {}".format(server.server_address))
    
    ser.write(b'r'); ser.write(b'g')
    n=1

    server.serve_forever()
    