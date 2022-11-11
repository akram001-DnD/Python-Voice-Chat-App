# This is server code to send video and audio frames over TCP

import socket
import threading, pyaudio,pickle,struct

host_name = socket.gethostname()
host_ip = '0.0.0.0'#  socket.gethostbyname(host_name)
print(host_ip)
port = 9001

def audio_stream():
    s = socket.socket()
    s.bind((host_ip, (port-1)))

    s.listen(5)

    print('server listening at',(host_ip, (port-1)))
   
    

    conn,addr = s.accept()
 
    data = None
    while True:
        if conn:
            try:
                while True:
                    data = conn.recv(1024)
                    conn.sendall(data)
            except:
                print("connection was lost by: ",addr[0])
                break
                
t1 = threading.Thread(target=audio_stream, args=())
t1.start()

