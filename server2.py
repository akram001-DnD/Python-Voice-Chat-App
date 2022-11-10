import socket
import sys
from threading import Thread
import time

list_of_clients = []
all_addrs = []
host = "0.0.0.0"
port = 9001
# Create Socket
def create_socket():
    try:
        global s
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error as msg:
        print("Socket creation error: ", str(msg))

#! Binding Socket and listening for connection
def bind_socket():
    try:
        global s
        print("Binding to port: ",str(port))
        s.bind((host,port))
        s.listen(3)
    except socket.error as msg:
        print("Socket creation error: ", str(msg), "\n" , "Retrying...")
        bind_socket()


def send_voice(conn,voice):
    while True:
        try:
            conn.send(voice)
        except KeyboardInterrupt:
            s.close()
        except OSError:
            s.close()


#* Handling connection from multiple clients
def launch_lobby(conn,addr):
    while True:
        try:
            voice = conn.recv(1024)
            print("Connection has been established! IP: ", addr[0])
            list_of_clients.append(conn)
            all_addrs.append(addr)

            for client in list_of_clients:
                if conn != client:
                    print(client)
                    try:
                        send_voice(client,voice)
                    except:
                        print(f"Connection with {client[0]} have been lost...")
                        

        except:
            print("Error Accepting Connections")
            continue


            
def list_connections():
    for i,c in enumerate(list_of_clients):
        results = str(i) + ' ' + str(all_addrs[i][0] + ' ' + str(list_of_clients[i][0]) + "\n")
        print("----Clients----" + "\n" + results)

 

def main():
    create_socket()
    bind_socket()
    while True:
        try:
            conn, addr = s.accept()
            thrd1 = Thread(target=start_program, args=(conn,addr))
            thrd1.start()
        except KeyboardInterrupt:
            s.close()
            break

def start_program(conn,addr):
    launch_lobby(conn,addr)

main()

 