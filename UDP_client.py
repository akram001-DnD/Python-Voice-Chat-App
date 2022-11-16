# Welcome to PyShine
# This is client code to receive video and audio frames over UDP

import socket
import threading,  pyaudio, time, queue
import sys
import numpy as np
import pickle
########################
#Jotar

####### wait for unreal client to give us the server info
#PlayerInfo = {"PlayerId":PlayerId,"type":"voiceMessage", ,"HostAddress","64.44.97.254", "TargetIds":[1,2,7],"Volume":[0.5,0.2,1.0] }
#send PlayerInfo to the server

######################
# For details visit: www.pyshine.com  
UDP_port = 9633
TCP_port = 9632

ID = "Drogba"
target_IDs = [["Roberto", 0.7]]

PlayerInfo = {"ID":ID, "type": "voiceMsg","HostAddress":"64.44.97.254","TargetIDs":target_IDs }
# host_ip = PlayerInfo["HostAddress"]
host_ip="192.168.1.41"

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
        chunk = np.frombuffer(data, dtype = np.int16)
        chunk = chunk * volume
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
            if PlayerInfo['type'] == "voiceMsg":
                voice = record.read(CHUNK)
                data = [PlayerInfo, voice]
                data=pickle.dumps(data)
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
        frame = pickle.loads(frame)
        msg, vol, type = frame
        if type == "voiceMsg":
            voice = set_volume(msg, vol)
            hear.write(voice)




t1 = threading.Thread(target=audio_stream_UDP, args=())
t1.start()

