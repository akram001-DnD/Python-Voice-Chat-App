# Welcome to PyShine
# This is client code to receive video and audio frames over UDP

import socket
import threading,  pyaudio, time, queue
import sys
import numpy as np

host_name = socket.gethostname()
host_ip = '192.168.1.41'
# host_ip="64.44.97.254"
print(host_ip)
port = 9633
# For details visit: www.pyshine.com

def audio_stream_UDP():
    BUFF_SIZE = 65536
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
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


    # answer,_ = s.recvfrom(BUFF_SIZE)
    # print(answer.decode())
    q = queue.Queue(maxsize=10000)


    def set_volume(data, volume):
        sound_level = (volume / 100.)
        chunk = np.fromstring(data, np.int16)
        chunk = chunk * sound_level
        data = chunk.astype(np.int16)
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
            data = set_volume(data, 100)
            try:
                s.sendto(data,(host_ip, port))
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
    name = "Drogba"
    s.sendto(name.encode(),(host_ip, port))

    t1 = threading.Thread(target=getAudioData, args=())
    t1.start()
    t2 = threading.Thread(target=sendAudioData, args=())
    t2.start()
    # t3 = threading.Thread(target=send_conn_check_msg, args=())
    # t3.start()

    # time.sleep(5)


    while True:
        frame = q.get()
        hear.write(frame)




t1 = threading.Thread(target=audio_stream_UDP, args=())
t1.start()


