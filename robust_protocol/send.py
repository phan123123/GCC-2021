#! /usr/bin/env python3

import os, sys, time, signal
import socket
import random

Taro = '169.254.155.219'
Hanako = '169.254.229.153'

if sys.argv[1] == 'Taro':
    SRC_IP = Taro
    DST_IP = Hanako
elif sys.argv[1] == 'Hanako':
    SRC_IP = Hanako
    DST_IP = Taro
elif sys.argv[1] == 'local':
    SRC_IP = 'localhost'
    DST_IP = 'localhost'

SRC_PORT = 50000
DST_PORT = 50002

SRC = (SRC_IP, SRC_PORT)
DST = (DST_IP, DST_PORT)


#header
FILENO_SIZE = 2
PKTNO_SIZE = 1
HEADER_SIZE = FILENO_SIZE + PKTNO_SIZE

#file size
FILE_NUM = 1000
FILE_SIZE = 102400
SEC_SIZE = 25
DATA_SIZE = FILE_SIZE//SEC_SIZE
PKT_SIZE = FILE_SIZE//SEC_SIZE + HEADER_SIZE
RECV_SIZE = 300
SPLIT_NUM = 10

SLEEP_TIME = 0.001
INTERRUPT_TIME = 0.005
#get files
DATA_PATH = "/home/pi/robust/data/"
data_files = os.listdir(DATA_PATH)

udp_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_recv.bind(SRC)

raws = [[] for _ in range(FILE_NUM)]
priority_pkts = set()
priority_pktss = set()
#interrupt func
def recv_cannot_send(arg1, arg2):
    #recv packete
    recv_binary_data, recv_addr = udp_recv.recvfrom(RECV_SIZE)
    
    start = 0
    end = HEADER_SIZE
    for i in range(50):
        fileno, pktno = int.from_bytes(recv_binary_data[start:start+FILENO_SIZE], 'little'),int.from_bytes(recv_binary_data[start+FILENO_SIZE:end], 'little')

        priority_pkts.add((fileno,pktno))

        start = end
        end = start + HEADER_SIZE
    
signal.signal(signal.SIGALRM, recv_cannot_send)
signal.setitimer(signal.ITIMER_REAL, INTERRUPT_TIME, INTERRUPT_TIME)

for fileno, data_file in enumerate(data_files[:FILE_NUM]):
    #read file
    f = open(DATA_PATH+data_file,'rb')
    send_data = f.read()
            
    #init
    start = 0
    end = DATA_SIZE
    recv_data = ""
    for pktno in range(SEC_SIZE):

        #make packet
        header = fileno.to_bytes(FILENO_SIZE,'little') + pktno.to_bytes(PKTNO_SIZE,'little')
        raw = header + send_data[start:end]

        raws[fileno].append(raw)

        #set next packet
        start = end
        end = start + DATA_SIZE

    #close file
    f.close()    

for fileno in range(FILE_NUM):
    for pktno in range(SEC_SIZE):
        #send  packet
        priority_pktss |= priority_pkts
        priority_pktss &= priority_pkts

        if not priority_pktss:
            udp_send.sendto(raws[fileno][pktno], DST)
            #time.sleep(SLEEP_TIME)
            priority_pkts.discard((fileno, pktno))
            print("[*] Sended Data : File {} Pkt {} To {}".format(fileno, pktno, DST_IP))
        #priority_pktss.discard((fileno, pktno))
        for priority_fileno, priority_pktno in priority_pktss:
            udp_send.sendto(raws[priority_fileno][priority_pktno], DST)
            priority_pkts.discard((priority_fileno, priority_pktno))
            print("[*] Sended Data : File {} Pkt {} To {}".format(priority_fileno, priority_pktno, DST_IP))


while True:
    priority_pktss |= priority_pkts
    priority_pktss &= priority_pkts

    for priority_fileno, priority_pktno in priority_pktss:
        udp_send.sendto(raws[priority_fileno][priority_pktno], DST)
        priority_pkts.discard((priority_fileno, priority_pktno))
        time.sleep(SLEEP_TIME)
        
