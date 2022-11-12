# This is server code to send video and audio frames over TCP

import socket
import threading

host_name = socket.gethostname()
host_ip = '0.0.0.0'
print(host_ip)
port = 9001
clients_list = []
addrs_list = []

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
                clients_list.remove(conn)
                addrs_list.remove(addr)
                break
            for i,client in enumerate(clients_list):
                if client != conn:
                    try:
                        client.sendall(data)  
                    except:
                        print("connection was lost by: ",addr)
                        client.close()
                        clients_list.pop(i)
                        addrs_list.pop(i)
                        print(f"clients list: {addrs_list}")
                        break
                

def main():
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
            pass
            

main()