# Welcome to PyShine
# This is client code to receive video and audio frames over UDP

import socket
import threading,  pyaudio, time, queue
import sys
import numpy as np

host_name = socket.gethostname()
host_ip = '192.168.1.41'
# host_ip="64.44.97.254"
UDP_port = 9633
TCP_port = 9632
ID = "bbb"
# For details visit: www.pyshine.com



def audio_stream_UDP():
    BUFF_SIZE = 65536
    #! Initializing UDP Connection
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
    print(f"Connected to server {host_ip}:{UDP_port} ")

    #! Initializing TCP Connection
    try:
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        print("Socket creation error: ", str(msg))
    try:
        tcp.connect((host_ip,TCP_port))
    except ConnectionRefusedError:
        print("This Server Is Dead!, Try Again Later.")
        sys.exit()
    except OSError:
        print("Unknown Error Happened!, Connection Closed.")
        sys.exit()
    tcp.send(ID.encode())

    p = pyaudio.PyAudio()
    CHUNK = 10*1024
    hear = p.open(format=p.get_format_from_width(2),
					channels=2,
					rate=44100,
					output=True,
					frames_per_buffer=CHUNK)
                    
    record = p.open(format=p.get_format_from_width(2),
					channels=2,
					rate=44100,
					input=True,
					frames_per_buffer=CHUNK)			


    # answer,_ = udp.recvfrom(BUFF_SIZE)
    # print(answer.decode())
    q = queue.Queue(maxsize=10000)


    def set_volume(data, volume):
        sound_level = (volume / 100.)
        chunk = np.frombuffer(data, dtype = np.int16)
        chunk = chunk * sound_level
        data = chunk.astype(np.int16)
        data = data.tobytes()      # Activate this for recieved audio
        return data


    def getAudioData():
        while True:
            try:
                frame,_= s.recvfrom(BUFF_SIZE)
                q.put(frame)
                # print('[Queue size while loading]...',q.qsize())
            except:
                s.close()
                print('Audio closed')
                sys.exit()

    def sendAudioData():
        while True:
            data = record.read(CHUNK)
            try:
                s.sendto(data,(host_ip, UDP_port))
            except OSError:
                sys.exit()
  

    # def send_conn_check_msg():
    #     while True:
    #         data = s.recvfrom(BUFF_SIZE)
    #         try:
    #             if data.decode() == "Still Connected?":
    #                 s.sendto("Still Connected".encode(),(host_ip, port))
    #         except UnicodeDecodeError:
    #             pass
    
    s.sendto(ID.encode(),(host_ip, UDP_port))
    msg, _ = s.recvfrom(BUFF_SIZE)
    print(msg.decode())
    t1 = threading.Thread(target=getAudioData, args=())
    t1.start()
    t2 = threading.Thread(target=sendAudioData, args=())
    t2.start()
    # t3 = threading.Thread(target=send_conn_check_msg, args=())
    # t3.start()

    # time.sleep(5)


    while True:
        frame = q.get()
        frame = set_volume(frame, 200)
        hear.write(frame)




t1 = threading.Thread(target=audio_stream_UDP, args=())
t1.start()


