# This is server code to send video and audio frames over UDP

import socket
import threading,  pyaudio, time
import math
import sys

host_name = socket.gethostname()
host_ip = '0.0.0.0'#  socket.gethostbyname(host_name)
print(host_ip)
port = 9633
clients_list = []
addrs_list = []
IDs_list = []
# For details visit: www.pyshine.com

def audio_stream_UDP():

    BUFF_SIZE = 65536
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)

    s.bind((host_ip, (port)))
    CHUNK = 10*1024
    p = pyaudio.PyAudio()
    print('server listening at',(host_ip, (port)))



    # def conn_check():
    #     while True:
    #         time.sleep(5)
    #         for client in clients_list:
    #             s.sendto("Still Connected?".encode() ,client)
    #             msg,_ = s.recvfrom(BUFF_SIZE)

    #             t_end = time.time() + 60 * 15
    #             while time.time() < t_end:
    #                 if msg == b"Still Connected":
    #                     break
    #             clients_list.remove(client)


    while True:
        data = None
        try:
            data, addr = s.recvfrom(BUFF_SIZE)
        except ConnectionResetError:
            pass
        
        if  isinstance(data,int):
            print("it is integer")

        if addr not in addrs_list:
            data = data.decode()
            if data not in clients_list:
                print(f'[GOT connection from]... {addr}, Name is: {data}')
                s.sendto(f"Server Message: You Have been Connected: {data}".encode(),addr)   
                addrs_list.append(addr)
                clients_list.append(data)
            elif data in clients_list:
                index = clients_list.index(data)
                clients_list.pop(index)
                addrs_list.pop(index)
                print(f'[GOT connection from]... {addr} Name is: {data}')
                s.sendto(f"Server Message: You Have been Connected: {data}".encode(),addr)   
                addrs_list.append(addr)
                clients_list.append(data)
            print(clients_list,"   ",addrs_list)
            continue

        if data is not None:
            # s.sendto(data,addr)  #* This is just to test the sound
            # time.sleep(0.1)
            for client in addrs_list:
                if addr != client:
                    s.sendto(data,client)
                    time.sleep(0.1) # Here you can adjust it according to how fast you want to send data keep it > 0
                    


t1 = threading.Thread(target=audio_stream_UDP, args=())
t1.start()

