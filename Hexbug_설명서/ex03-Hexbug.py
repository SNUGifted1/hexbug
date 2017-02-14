import argparse
import numpy as np
import matplotlib.pyplot as plt
import bci_workshop_tools as BCIw

from pythonosc import dispatcher
from pythonosc import osc_server

data = np.zeros([1,5]) 

def eeg_handler(unused_addr, args, TP9, AF7, AF8, TP10, Status):
    # OSC가 /muse/eeg 주소의 데이터를 찾으면 실행되는 함수이다. 
    
    global data
    temp = np.array([[int(Status), int(TP10), int(AF8), int(AF7), int(TP9)]])
    data = np.concatenate((data, temp), axis=0)


def getdata(seconds, params):
    
    global data
    # Size of data requested
    n_samples = int(round(seconds * params['sampling frequency']))
    data_buffer = -1 * np.ones((n_samples, 1)) 
 

    while (data_buffer[0, 0]) < 0 : #While the first row has not been rewriten
        server.handle_request()
        new_samples = data.shape[0]
        data_buffer = np.concatenate((data_buffer, data), axis =0)
        data_buffer = np.delete(data_buffer, np.s_[0:new_samples], 0)
        data = np.delete(data, np.s_[0:n_samples], 0)

    return data_buffer
        
     
if __name__ == "__main__":

    # cmd에서 파일명 뒤에 입력된 ip, port를 파악하여 서버 주소로 넘겨준다.

    parser = argparse.ArgumentParser()

    parser.add_argument("--ip", default="0.0.0.0", help="The ip to listen on")

    parser.add_argument("--port", type=int, default=5040, help="The port to listen on")

    args = parser.parse_args()


    dispatcher = dispatcher.Dispatcher()

    dispatcher.map("/debug", print)

    dispatcher.map("/muse/elements/blink", eeg_handler1, "Blink")
    dispatcher.map("/muse/elements/jaw_clench", eeg_handler2, "Jaw_clench")

    # 서버를 정의하고 서버를 실행한다. 

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)

    print("Serving on {}".format(server.server_address))
    
    try:
        while 1: 
            eeg_data = getdata(shift_secs, params) # Obtain EEG data from MuLES  
           
            plt.pause(0.001)
                       
    except KeyboardInterrupt:
        server.shutdown()
   
    finally:
        server.shutdown()

