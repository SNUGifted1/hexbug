import argparse
import numpy as np
import matplotlib.pyplot as plt
import bci_workshop_tools as BCIw

import serial 
PORT = 'COM3'  # 아두이노 연결 포트
BAUDRATE = 9600  # 아두이노 프로그램 내의 RATE와 일치해야 함

from pythonosc import dispatcher
from pythonosc import osc_server

data = np.zeros([1,5]) 

def eeg_handler(unused_addr, args, TP9, AF7, AF8, TP10, Status):
      
    global data
    temp = np.array([[int(Status), int(TP10), int(AF8), int(AF7), int(TP9)]])
    data = np.concatenate((data, temp), axis=0)


def getdata(seconds, params):
    
    global data
    # Size of data requested
    n_samples = int(round(seconds * params['sampling frequency']))
    n_columns = len(params['data format'])
    data_buffer = -1 * np.ones((n_samples, n_columns)) 
 

    while (data_buffer[0, n_columns - 1]) < 0 : #While the first row has not been rewriten
        server.handle_request()
        new_samples = data.shape[0]
        data_buffer = np.concatenate((data_buffer, data), axis =0)
        data_buffer = np.delete(data_buffer, np.s_[0:new_samples], 0)
        data = np.delete(data, np.s_[0:n_samples], 0)

    return data_buffer
        
     
if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--ip", default="0.0.0.0", help="The ip to listen on")

    parser.add_argument("--port", type=int, default=5041, help="The port to listen on")

    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()

    dispatcher.map("/debug", print)

    dispatcher.map("/muse/eeg", eeg_handler, "EEG")

    server = osc_server.ThreadingOSCUDPServer((args.ip, args.port), dispatcher)

    m_flag = 0
    ser = serial.Serial(PORT, BAUDRATE)
    ser.write(b'r'); ser.write(b'g')

    #%% Set the experiment parameters
    params = {'names of channels':['Status', 'TP10', 'AF8', 'AF7', 'TP9'], 'data format':[0,0,0,0,0], 'sampling frequency':256}

    fs = params['sampling frequency']

    training_secs = 10
    win_test_secs = 3    # Length of the Test Window in seconds
    overlap_secs = 0.5   # Overlap between two consecutive Test Windows
    shift_secs = win_test_secs - overlap_secs   
    eeg_buffer_secs = 30  # Size of the EEG data buffer (duration of Testing section) 
    
    # Record training data
    
    # Record data for mental activity 0

    print (chr(7),'Record data for mental activity 0 for %s second' %training_secs)
    eeg_data0 = getdata(training_secs, params)
    
    # Record data for mental activity 1
    print (chr(7),'Record data for mental activity 1 for %s second' %training_secs)
    eeg_data1 = getdata(training_secs, params)    
    
    # Divide data into epochs
    eeg_epochs0 = BCIw.epoching(eeg_data0, win_test_secs * params['sampling frequency'], 
                                            overlap_secs * params['sampling frequency'])
    eeg_epochs1 = BCIw.epoching(eeg_data1, win_test_secs * params['sampling frequency'],    
                                            overlap_secs * params['sampling frequency'])
    
    #%% Compute features
    
    feat_matrix0 = BCIw.compute_feature_matrix(eeg_epochs0, params['sampling frequency'])
    feat_matrix1 = BCIw.compute_feature_matrix(eeg_epochs1, params['sampling frequency'])
    
    #%% Train classifier    

    [classifier, mu_ft, std_ft] = BCIw.classifier_train(feat_matrix0, feat_matrix1, 'svm')
    
    #%% Initialize the buffers for storing raw EEG and decisions
    
    eeg_buffer = np.zeros((params['sampling frequency']*eeg_buffer_secs, len(params['data format']))) 
    decision_buffer = np.zeros((30,1))

        
       
    print("Serving on {}".format(server.server_address))


    try:
        while 1: 

            """ 1- ACQUIRE DATA """
            eeg_data = getdata(shift_secs, params) # Obtain EEG data from MuLES  
            eeg_buffer = BCIw.updatebuffer(eeg_buffer, eeg_data) # Update EEG buffer

             # Get newest "testing samples" from the buffer        
            test_data = BCIw.getlastdata(eeg_buffer, win_test_secs * params['sampling frequency'])
            
            
            """ 2- COMPUTE FEATURES and CLASSIFY"""            
            # Compute features on "test_data"
            feat_vector = BCIw.compute_feature_vector(test_data, params['sampling frequency'])
            y_hat = BCIw.classifier_test(classifier, feat_vector, mu_ft, std_ft)

            print(y_hat)
                       
            if y_hat == 1:
                if m_flag==0:
                    print ("                 Go forward!")
                    ser.write(b'G')
                    m_flag=1
                else:
                    if m_flag==1:
                        print ("                 Stop!")
                        ser.write(b'g')    
                        m_flag=0
                               
                    
                       
    except KeyboardInterrupt:
        server.shutdown()
   
    finally:
        server.shutdown()


