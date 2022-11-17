# Welcome to PyShine
# This is client code to receive video and audio frames over UDP

import socket,json
import threading,  pyaudio, time, queue
import sys
import numpy as np
import pickle
from p2p_Library import AudioReceiver, AudioSender




########################
######################
# For details visit: www.pyshine.com  



PlayerInfo = {}



def ReceiveTCPFromUnreal():

    host = "0.0.0.0"
    UE_TCP_port = 5001  

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    sock.bind((host, UE_TCP_port))  
    print("Connection bind: " ,UE_TCP_port)
    
    sock.listen()   # configure how many client the server can listen simultaneously
    conn, address = sock.accept()  
    print("Connection from: " ,address)
    while True:
        data= None
        # receive data stream. it won't accept data packet greater than 1024 bytes
        data = conn.recv(1024).decode()
        if data is None:
            # if no data was received then stop the Iteration
            print("data invalid!")
            continue
        print("from connected user: " + str(data))
        data = input(' -> ')
        try:
            conn.send(data.encode())  # send data to the client
        except ConnectionResetError:
            conn.close()  




def ReceiveUDPFromUnreal():
    global PlayerInfo
    BUFF_SIZE = 1024
    UE_UDP_port=63071
    
    host_ip = '0.0.0.0'
    target_IDs = [{"target_id": 1, "volume": 0.7}]  
    PlayerInfo = {"player_id":1, "type": "voiceMsg","recording":True,"HostAddress":"64.44.97.254","TargetIDs":target_IDs }
    time.sleep(1)
    UESocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    UESocket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
    UESocket.bind((host_ip, (UE_UDP_port)))
    print('UDP server listening at',(host_ip, (UE_UDP_port)))
    print(f"listen from unreal client {host_ip}:{UE_UDP_port}")

    while True:
        data = None
        try:
            data, addr = UESocket.recvfrom(BUFF_SIZE)
        except ConnectionResetError:
            continue
        if data is None:
            print('null data erceived from unreal!')
            continue

        PlayerInfo = pickle.loads(data)
        
       
        type=PlayerInfo["type"]
        if type !="voiceMsg":
            print(f'type <<{type}>> is not valid !')
            continue
        micOn=PlayerInfo["recording"]
        
        #print('micOn:: ',micOn)
        #print('PlayerInfoJson:: ',PlayerInfo)
        PlayerInfo=PlayerInfo

def audio_stream_UDP():
    target_IDs = [{"target_id": "1", "volume": 2}]  
    PlayerInfo = {}
    PlayerInfo = {"player_id":"1", "type": "global_voice","recording":True,"HostAddress":"64.44.97.254","TargetIDs":target_IDs }
    # PlayerInfo = {"player_id":1, "type": "p2p_call","recording":False,"HostAddress":"64.44.97.254","TargetIDs":target_IDs, "p2p_dest":{"addr":"192.168.1.41","accepted?":False} }
    host_ip="64.44.97.254"
    UDP_port = 9009
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


    def set_volume(data, volume):
        chunk = np.frombuffer(data, dtype = np.int16)
        chunk = chunk * volume
        data = chunk.astype(np.int16)
        data = data.tobytes()      # Activate this for recieved audio
        return data

    def sendAudioData():
        while True: 
            type = PlayerInfo['type']
            if type == "global_voice":
                if PlayerInfo =={}:
                    continue
                micOn=PlayerInfo["recording"]
                type = PlayerInfo['type']
                if micOn:
                    voice = record.read(CHUNK)
                    data =[PlayerInfo, voice]
                    data=pickle.dumps(data)
                    s.sendto(data,(host_ip, UDP_port))

                

    # def p2p():
    #     port = 4000

    #     type = PlayerInfo['type']
    #     if type == "p2p_call":
    #         reciever_ip = "192.168.1.41"
    #         alert =[PlayerInfo, "private_call"]
    #         alert=pickle.dumps(alert)
    #         s.sendto(alert,(rec, UDP_port))


        # t1 = threading.Thread(target=AudioReceiver, args=(reciever_ip, port))
        # t1.start()

        # t2 = threading.Thread(target=AudioSender, args=(reciever_ip, port))
        # t2.start()


############################### receive audio
    def recieveAudioData():
        while True:
            data = None
            try:
                data, _ = s.recvfrom(BUFF_SIZE)
            except ConnectionResetError:
                continue

            if data is None:
                continue
            #fill sender Info data
            SenderInfo = {}
            SenderInfo, voice = pickle.loads(data)
            if voice is None:
                continue

            sender_id = SenderInfo['sender_id']
            volume = SenderInfo['volume']
            type = SenderInfo['type']
            if type == "global_voice":
                voice = set_volume(voice, volume)
                hear.write(voice)
                #print("hear: ", voice)


    t1 = threading.Thread(target=sendAudioData, args=())
    t1.start()

    t2 = threading.Thread(target=recieveAudioData, args=())
    t2.start()




#ReceiveFromUnreal
#ReceiveTCPFromUnreal
# t3 = threading.Thread(target=ReceiveUDPFromUnreal, args=())
# t3.start()

# audio_stream_UDP()
t1 = threading.Thread(target=audio_stream_UDP, args=())
t1.start()







