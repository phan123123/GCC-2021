#! /usr/bin/env python3

import os, sys, time, signal
import socket

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


SRC_PORT = 50002
DST_PORT = 50000

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

SLEEP_TIME = 0.0005
INTERRUPT_TIME = 0.0005

#get files
RECV_PATH = "/home/pi/robust/data/"
os.makedirs(RECV_PATH, exist_ok=True)

#udp_recv 
udp_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_recv.bind(SRC)

#udp_send
udp_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

file_data = [[None for _ in range(SEC_SIZE)] for _ in range(FILE_NUM)]

#init
#last_fileno = -1
recv_data = "" 
#base_fileno = 0
recv_fileno = set()
comp_fileno = set()
not_recv_pkt = b''

def send_not_recv(arg1, arg2):
    global not_recv_pkt
    #print(not_recv_pkt)
    udp_send.sendto(not_recv_pkt, DST)
    not_recv_pkt = b''
    #time.sleep(SLEEP_TIME)

signal.signal(signal.SIGALRM, send_not_recv)
signal.setitimer(signal.ITIMER_REAL, INTERRUPT_TIME, INTERRUPT_TIME)

num = 0
while True:
    #send and recv packet
    recv_binary_data, recv_addr = udp_recv.recvfrom(PKT_SIZE)
    recv_header = recv_binary_data[:HEADER_SIZE]
    fileno, pktno = int.from_bytes(recv_header[:FILENO_SIZE], 'little'),int.from_bytes(recv_header[FILENO_SIZE:], 'little')
    
    print("[*] Comp {} :: Received Data : File {} Pkt {} From {}".format(len(comp_fileno),fileno, pktno, recv_addr))
    
    #create new file storage

    #add pkt to file storage
    file_data[fileno][pktno] = recv_binary_data[HEADER_SIZE:].decode()
    
    recv_fileno.add(fileno)
    
    for i in (recv_fileno - comp_fileno):
        if None not in file_data[i]:
            for s in file_data[i]:
                recv_data += s
            #print(recv_data)        
            #read file
            f = open(os.path.join(RECV_PATH, "recv"+str(num)),'w')
            #write file
            f.write(recv_data)
            #close file
            f.close()
            recv_data = ""
            comp_fileno.add(i)
            #base_fileno += 1
            print("[*] Write recv{} file! ".format(i))


        for pktno in [j for j in range(SEC_SIZE) if file_data[i][j] == None]:
            #print(pktno)
            not_recv_pkt += i.to_bytes(FILENO_SIZE,'little') + pktno.to_bytes(PKTNO_SIZE,'little')
            if len(not_recv_pkt) > RECV_SIZE:
                break


    num += 1

