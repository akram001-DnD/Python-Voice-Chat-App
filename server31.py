# This is server code to send video and audio frames over TCP

import socket
import threading, pyaudio,pickle,struct

host_name = socket.gethostname()
host_ip = '0.0.0.0'
print(host_ip)
port = 9001
clients_list = []
addrs_list = []

def audio_stream(conn,addr):
    clients_list.append((conn,addr))
    addrs_list.append(addr)
    data = None
    while True:
        if conn:
            try:
                while True:
                    data = conn.recv(1024)
                    for client in clients_list:
                        if client[0] != conn:
                            client[0].sendall(data)  
            except:
                print("connection was lost by: ",addr[0])
                print(f"clients list: {addrs_list}")
                client[0].close()
                clients_list.remove(client)
                addrs_list.remove(client[1])
                break
                

def main():
    global s
    s = socket.socket()
    s.bind((host_ip, port))
    s.listen(5)
    print('server listening at',(host_ip, port))
   
    
    while True:
        try:
            conn, addr = s.accept()
            print(f"Client {addr} Have been connected!")
            t1 = threading.Thread(target=audio_stream, args=(conn, addr))
            t1.start()
        except KeyboardInterrupt:
            s.close()
            break

main()