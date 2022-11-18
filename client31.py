import socket,os
import threading, wave, pyaudio, pickle,struct
import numpy as np
import time
import sys
stop_thread = threading.Event()
host_name = socket.gethostname()
host_ip="64.44.97.254"
# host_ip = '192.168.1.41'
port = 9001
CHUNK = 32
rate = 44100
format = pyaudio.paInt16
p = pyaudio.PyAudio()



def set_volume(data, volume):
        chunk = np.frombuffer(data, dtype = np.int16)
        chunk = chunk * volume
        data = chunk.astype(np.int16)
        data = data.tobytes()      # Activate this for recieved audio
        return data

def stop_streaming(stream):
    stream.stop_stream()
    stream.close()
    p.terminate()



def create_socket():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error as msg:
        print("Socket creation error: ", str(msg))


def audio_recieve():
    global s
    stream = p.open(format=format,
    channels=2,
    rate=rate,
    output=True,
    frames_per_buffer=CHUNK)

    print('server listening at ',port)
    print("CLIENT CONNECTED TO ",host_ip)
    while True:
        try:
            voice = s.recv(CHUNK)
            voice = set_volume(voice, 3)
            stream.write(voice)
        except ConnectionResetError:
            print("Connection to the server was lost, Reconnecting Again...")
            sys.exit()




def audio_send():
    global s
    stream = p.open(format=format,
                channels=2,
                rate=44100,
                input=True,
                frames_per_buffer=CHUNK)

    data = None
    while True:
        if s:
            data = stream.read(CHUNK)
            try:
                s.send(data)
            except ConnectionResetError:
                print("Connection to the server was lost, Reconnecting Again...")
                sys.exit()
            
            
    
                

def main():
    global s
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        print("Socket creation error: ", str(msg))
    try:
        s.connect((host_ip,port))
    except ConnectionRefusedError:
        print("This Server Is Dead!, Try Again Later.")
        sys.exit()
    except OSError:
        print("Unknown Error Happened!, Connection Closed.")
        sys.exit()
    msg = None
    while True:
        msg = s.recv(1024)   
        print(msg.decode(),"\n") 
        if msg is not None:
            # id_sent = input("What is your ID: ")
            id_sent = "Pepsi"
            s.send(id_sent.encode())
            break


    t1 = threading.Thread(target=audio_send, args=())
    t1.start()

    t2 = threading.Thread(target=audio_recieve, args=())
    t2.start()

main()