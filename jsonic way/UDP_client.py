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
UDP_port = 9009
TCP_port = 9632

ID = 0



host_ip="192.168.1.41"

def audio_stream_UDP():


    BUFF_SIZE = 65536
    #! Initializing UDP Connection

    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
 
    # s.sendto("connected".encode(),(host_ip, UDP_port))
    s.connect((host_ip, UDP_port))
    print(f"Connected to server {host_ip}:{UDP_port}")

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
            frame = None
            try:
                frame,_= s.recvfrom(BUFF_SIZE)
                q.put(frame)
            except ConnectionResetError:
                s.close()
                print('Audio closed')
                sys.exit()

    def sendAudioData():
        PlayerInfo = {}
        target_IDs = [{"target_id": "2", "volume": 0.7}]  
        PlayerInfo = {"ID":"1", "type": "voiceMsg","HostAddress":"64.44.97.254","TargetIDs":target_IDs }
        type = PlayerInfo["type"]
        while True:
            if type == "voiceMsg":
                voice = record.read(CHUNK)
                data =[PlayerInfo, voice]
                data=pickle.dumps(data)
                try:
                    s.sendto(data,(host_ip, UDP_port))
                except OSError as msg:
                    print("sendAudioData: ", msg)
                    sys.exit()
    

    # def send_conn_check_msg():
    #     while True:
    #         data = s.recvfrom(BUFF_SIZE)
    #         try:
    #             if data.decode() == "Still Connected?":
    #                 s.sendto("Still Connected".encode(),(host_ip, port))
    #         except UnicodeDecodeError:
    #             pass
    
    # s.sendto(ID.encode(),(host_ip, UDP_port))
    # msg, _ = s.recvfrom(BUFF_SIZE)
    t1 = threading.Thread(target=getAudioData, args=())
    t1.start()

    t2 = threading.Thread(target=sendAudioData, args=())
    t2.start()
    # t3 = threading.Thread(target=send_conn_check_msg, args=())
    # t3.start()

    # time.sleep(5)


    while True:
        frame = q.get()
        senderinfo = {}
        senderinfo, msg = pickle.loads(frame)

        sender_id = senderinfo['sender']
        volume = senderinfo['volume']
        type = senderinfo['type']
        if type == "voiceMsg":
            voice = msg
            voice = set_volume(voice, volume)
            hear.write(voice)



# audio_stream_UDP()
t1 = threading.Thread(target=audio_stream_UDP, args=())
t1.start()


