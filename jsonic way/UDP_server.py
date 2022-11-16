# This is server code to send video and audio frames over UDP

import socket, threading, time, pickle

host_name = socket.gethostname()
host_ip = '0.0.0.0'#  socket.gethostbyname(host_name)
print(host_ip)
UDP_port = 9009
TCP_port = 9632
clients_list = []
addrs_list = []
IDs_list = []




def audio_stream_UDP():
    playersInfo={}
    BUFF_SIZE = 65536
    #! Initializing UDP server

    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
    s.bind((host_ip, (UDP_port)))
     
    print('UDP server listening at',(host_ip, (UDP_port)))



    while True:
        data = None
        try:
            data, addr = s.recvfrom(BUFF_SIZE)
        except ConnectionResetError:
            continue

        if data is None:
            continue

        playerInfo = {}
        playerInfo, msg = pickle.loads(data)
        sender_id = playerInfo['ID']


        if sender_id not in playersInfo.keys():
            playersInfo[sender_id] = addr
            print('if section:: ',playersInfo)

        elif  sender_id in playersInfo.keys() and addr not in playersInfo.values():
            playersInfo[sender_id] = addr
            print('elif section:: ',playersInfo)
            
        
            
        type = playerInfo['type']
        if type == "voiceMsg":
            voice = msg
            targetIDs = playerInfo['TargetIDs'] # targetsIDs list
            for target in targetIDs:   # target JSON
                target_id = target['target_id']
                if target_id in list(playersInfo.keys()):
                    volume = target['volume']
                    target_ip = playersInfo[target_id]

                    # Initilize JSON to send to the client
                    targetInfo = {}
                    targetInfo['sender'] = sender_id
                    targetInfo['volume'] = volume
                    targetInfo['type'] = type
                    
                    frame = [targetInfo, voice]
                    frame = pickle.dumps(frame)
                    s.sendto(frame, target_ip)
            time.sleep(0.1)

            
        # for Info in PlayersInfo:
        #     if Info.ClientAddress == addr:
        #         PlayerInfo=Info
        # IdsSendTo=[]
        # AddrSendTo=[]
        # IdsSendTo=PlayerInfo.TargetIds
        # if    PlayerInfo !=None:     
        #         for Info in PlayersInfo:
        #             if  Info.PlayerId in IdsSendTo:
        #                 AddrSendTo.append(Info.ClientAddress)


                    


t1 = threading.Thread(target=audio_stream_UDP, args=())
t1.start()
time.sleep(0.2)


