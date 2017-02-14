# -*- coding: utf-8 -*-

__author__ = 'Jongjin Kim'

"""
Record data from the Neurosky Mindwave mobile.
"""

import os
from consider import Consider
import datetime
import time
import serial  # 시리얼 라이브러리 문제 생기는 경우 실행 폴더로 라이브러리 복사

ONOFF = ["OFF","ON"]
CWD = os.path.abspath(os.getcwd())
PORT = 'COM3'  # 아두이노 연결 포트
BAUDRATE = 9600  # 아두이노 프로그램 내의 RATE와 일치해야 함

def record(out):
    con = Consider() # 뉴로스카이
#    packet = con.get_packet()
#    print packet
    meditation_threshold = 80
    attention_threshold = 60
    m_flag = 0  # 0 - off, 1 - on
    a_flag = 0  # 0 - off, 1 - on
    
    print "waiting for BCI headset signal "
    
    ser = serial.Serial(PORT, BAUDRATE) #파이썬과 아두이노 연결

    for p in con.packet_generator(): # 뉴로스카이
        data = map(str, [datetime.datetime.now(), p.delta, p.theta, p.low_alpha, p.high_alpha, p.low_beta, p.high_beta, p.low_gamma, p.high_gamma, p.attention, p.meditation, p.poor_signal])
        out.write(','.join(data)) # 데이터 쌓기
        out.write('\n') # 행바꿈

        if p.poor_signal == 0:
            print "meditation: %s / 100 | attention : %s / 100   | Green : %s  | Red : %s  " % (p.meditation, p.attention, ONOFF[m_flag], ONOFF[a_flag])
            if (p.meditation > meditation_threshold):
                print "       Deep Meditation ..._(_-_)_"
                if(m_flag==0):
#                    print "                 Green ON "
                    ser.write('G')
                    m_flag = 1
#                    sound.play_meditation_sound()
            else:
                if(m_flag==1):
                    m_flag = 0
#                    print "                 Green OFF "
                    ser.write('g')

            if p.attention > attention_threshold:
                print "        High Attention!!!!!"
                if(a_flag==0):
#                    print "                 Red ON "
                    ser.write('R')
                    a_flag=1
#                    sound.play_attention_sound()
            else:
                if(a_flag==1):
                    a_flag = 0
#                    print "                 Red OFF "
                    ser.write('r')
        else:
            print "no signal yet"


def main():
    now = time.localtime();
#    day = "%04d%02d%02d" % (now.tm_year, now.tm_mon, now.tm_mday)
    tm = "%02d%02d" % (now.tm_hour, now.tm_min)
#    out = open("%s/data/%s/mindwave_%s.csv" % (CWD, day, tm), 'wb')
    out = open("%s/mindwave_%s.csv" % (CWD, tm), 'wb')
    header = map(str, ['Time', 'Delta', 'Theta', 'Low_Alpha', 'High_Alpha', 'Low_Beta', 'High_Beta', 'Low_Gamma', 'High_Gamma', 'Attention', 'Meditation', 'Signal'])
    out.write(','.join(header))
    out.write('\n')
    try:
        record(out)
    except KeyboardInterrupt:
        print "Interrupted by User"
        if hasattr(out, 'close'):
            out.close()


if __name__ == '__main__':
    main()

