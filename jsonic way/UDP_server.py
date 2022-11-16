# This is server code to send video and audio frames over UDP

import socket, threading, time, pickle

host_name = socket.gethostname()
host_ip = '0.0.0.0'#  socket.gethostbyname(host_name)
print(host_ip)
UDP_port = 9633
TCP_port = 9632
clients_list = []
addrs_list = []
IDs_list = []
##################################
#receive from clients
#Jotar
#format example
#PlayerInfo = {"PlayerId":PlayerId,"type":"voiceMessage", ,"ClientAddress","14.45.117.204", "TargetIds":[1,2,7],"Volume":[0.5,0.2,1.0] }
#PlayersInfo ={"PlayerId",PlayerInfo}
# PlayersInfo = {}
# For details visit: www.pyshine.com


def check_connectivity():
    #! Initializing TCP server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host_ip, TCP_port))
    s.listen()
    print('TCP server listening at',(host_ip, (TCP_port)))

    def accepting_connections():
        while True:
            conn, addr = s.accept()
            ID = conn.recv(1024)
            ID = ID.decode()
            temp_arr = []
            for arr in clients_list:
                temp_arr.append(arr[1])
            if ID not in temp_arr:
                clients_list.append((conn,ID))

    def checking_connections():
        while True:
            time.sleep(5)
            for client in clients_list:
                conn = client[0]
                ID = client[1]
                try:
                    conn.send(b"boo!")
                except ConnectionResetError:
                    conn.close()
                    clients_list.remove(client)   
                    if ID in IDs_list:
                        index =  IDs_list.index(ID)
                        IDs_list.pop(index)
                        addrs_list.pop(index)

    t1 = threading.Thread(target=accepting_connections, args=())
    t1.start()

    t2 = threading.Thread(target=checking_connections, args=())
    t2.start()



# def ReceivePlayersInfo():
#     BUFF_SIZE = 65536
#     ws = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#     ws.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
#     ws.bind((host_ip, (UDP_port)))
#     print('UDP server listening at client infos :: ',(host_ip, (UDP_port)))
#     while True:
#         PlayerInfo = {}
#         data = None
#         try:
#             data, addr = ws.recvfrom(BUFF_SIZE)
#             #TODO: convert bytes to json
#             PlayersInfo[PlayerInfo.PlayerId]=PlayerInfo
#         except ConnectionResetError:
#             pass

def audio_stream_UDP():
    BUFF_SIZE = 65536
    #! Initializing UDP server
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
    s.bind((host_ip, (UDP_port)))
    print('UDP server listening at',(host_ip, (UDP_port)))


    # def conn_check():
    #     while True:
    #         time.sleep(5)
    #         for client in IDs_list:
    #             s.sendto("Still Connected?".encode() ,client)
    #             msg,_ = s.recvfrom(BUFF_SIZE)

    #             t_end = time.time() + 60 * 15
    #             while time.time() < t_end:
    #                 if msg == b"Still Connected":
    #                     break
    #             IDs_list.remove(client)


    while True:
        data = None
        try:
            data, addr = s.recvfrom(BUFF_SIZE)
        except ConnectionResetError:
            pass

        if addr not in addrs_list:
            playerID = data.decode()
            if playerID not in IDs_list:
                print(f'[GOT connection from]... {addr}, Name is: {playerID}')
                s.sendto(f"Server Message: You Have been Connected: {playerID}".encode(),addr)   
                addrs_list.append(addr)
                IDs_list.append(playerID)
            elif playerID in IDs_list:
                index = IDs_list.index(playerID)
                IDs_list.pop(index)
                addrs_list.pop(index)
                print(f'[GOT connection from]... {addr} Name is: {playerID}')
                s.sendto(f"Server Message: You Have been Connected: {playerID}".encode(),addr)   
                addrs_list.append(addr)
                IDs_list.append(playerID)
            print(IDs_list,"   ",addrs_list)
            print(clients_list)
            continue

        #TODO: define SendTo to sent voice to
        #first find the player id  of this audio sender
        if data is None:
            continue
        data = pickle.loads(data)
        playerInfo, msg = data
        type = playerInfo['type']
        if type == "voiceMsg":
            targetIDs = playerInfo['TargetIDs']
            for recepient in targetIDs:
                ID, vol = recepient
                if ID in IDs_list:
                    index = IDs_list.index(ID)
                    destination = addrs_list[index]
                    frame = [msg, vol, type]
                    frame = pickle.dumps(frame)
                    s.sendto(frame, destination)
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
check_connectivity()
# t2 = threading.Thread(target=check_connectivity, args=())
# t2.start()
