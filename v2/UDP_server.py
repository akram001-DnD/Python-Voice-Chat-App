# This is server code to send video and audio frames over UDP

import socket, threading, time, pickle

host_name = socket.gethostname()
host_ip = '0.0.0.0'#  socket.gethostbyname(host_name)
print(host_ip)
UDP_port = 9010
TCP_port = 9632
clients_list = []
addrs_list = []
IDs_list = []

#python UDP_server.py


def audio_stream_UDP():
    all_players={}
    BUFF_SIZE = 65536

    #! Initializing UDP server
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
    s.bind((host_ip, (UDP_port)))
    
    print('UDP server listening at',(host_ip, (UDP_port)))



    while True:
        data = None
        playerInfo = None
        compressed_voice = None
        try:
            data, addr = s.recvfrom(BUFF_SIZE)
        except ConnectionResetError:
            continue
        
        if data is None:
            continue
        
        playerInfo, compressed_voice = pickle.loads(data)
        if playerInfo is None: 
            continue
        
        #! DO NOT TOUCH THIS AGAIN
        #? This is essantial if a client is reconnecting to the server to make sure he is not registred to the list more than one time
        #* CHECKING IF THE CLIENT IS ALREADY REGISTRED IN OUR LIST
        sender_id = playerInfo['player_id']
        if sender_id not in all_players.keys():
            playerInfo["IpAddress"] = addr
            all_players[sender_id] = playerInfo
            print(f'Client {sender_id} :: {addr} Have Been Connected!')
            # print("if Section :: ",all_players)
            print(compressed_voice)
            continue
        elif sender_id in all_players.keys() and addr != all_players[sender_id]["IpAddress"]:
            all_players[sender_id]['IpAddress']=addr
            print(f'Client {sender_id} :: {addr} Have Reconnected!')
            # print("elif Section :: ",all_players)
            continue

        type = playerInfo['type']
        if type == "global_voice":
            targetsIDs = playerInfo['TargetIDs'] # targetsIDs list

            for PlayerTarget in targetsIDs:   # PlayerTarget JSON
                target_id = PlayerTarget['target_id']

                if target_id in list(all_players.keys()): 
                    volume = PlayerTarget['volume']
                    PlayerTargetAddress= all_players[target_id]['IpAddress'] #! "addr" is going to send, and "PlayerTargetAddress" is going to recieve

                    # Initilizing Sender INFO as JSON to send to the client
                    senderInfo = {}
                    senderInfo['sender_id'] = sender_id #! This "sender_id" is not Target's ID
                    senderInfo['volume'] = volume
                    senderInfo['type'] = type
                    
                    frame = [senderInfo, compressed_voice]
                    frame = pickle.dumps(frame)
                    s.sendto(frame, PlayerTargetAddress)
            time.sleep(0.1)

t1 = threading.Thread(target=audio_stream_UDP, args=())
t1.start()
time.sleep(0.2)


