# This is server code to send video and audio frames over TCP

import socket
import threading

host_name = socket.gethostname()
host_ip = '0.0.0.0'
print(host_ip)
port = 9001
clients_list = []
addrs_list = []
IDs_list = []

def audio_stream(conn,addr):
    clients_list.append(conn)
    addrs_list.append(addr)
    data = None
    while True:
        if conn:
            try:
                data = conn.recv(1024)
            except ConnectionResetError:
                print("connection was lost by: ",addr)
                conn.close()
                index = clients_list.index(conn)
                clients_list.remove(conn)
                addrs_list.remove(addr)
                IDs_list.pop(index)
                break
            for i,client in enumerate(clients_list):
                if client != conn:
                    try:
                        client.send(data)  
                    except:
                        print("connection was lost by: ",addr)
                        client.close()
                        clients_list.pop(i)
                        addrs_list.pop(i)
                        IDs_list.pop(i)
                        print(f"clients list: {addrs_list}")
                        break
                

def main():
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host_ip, port))
    s.listen(5)
    print('server listening at',(host_ip, port))
   
    
    while True:
        try:
            conn, addr = s.accept()
            print("Taking client ID...")
            conn.send("Extracting Client Information... ".encode())
            id = None
            while True:
                id = conn.recv(512)
                if id is not None:
                    id = id.decode()
                    IDs_list.append(id)
                    print(f"Client {id} : {addr} Have been connected!")
                    break
            t1 = threading.Thread(target=audio_stream, args=(conn, addr))
            t1.start()
        except KeyboardInterrupt:
            pass
            

main()