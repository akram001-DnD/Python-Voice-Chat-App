# This is server code to send video and audio frames over UDP

import socket
import threading,  pyaudio, time
import math
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


    data = None
    msg = None
    while True:
        msg,client_addr = s.recvfrom(BUFF_SIZE)
        if msg is not None:
            print('[GOT connection from]... ',client_addr,msg.decode())
            s.sendto(b"Server Message: You Have Connected",client_addr)
            clients_list.append(client_addr)
            while True:
                data, addr = s.recvfrom(BUFF_SIZE)
                for client in clients_list:
                    if addr != client_addr:
                        try:
                            s.sendto(data,client)
                            time.sleep(0.1) # Here you can adjust it according to how fast you want to send data keep it > 0
                            print(clients_list)
                        except:
                            print(f"Client {client} Disconnected!")
                            clients_list.remove(client)

t1 = threading.Thread(target=audio_stream_UDP, args=())
t1.start()

