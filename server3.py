# This is server code to send video and audio frames over TCP

import socket
import threading, wave, pyaudio,pickle,struct

host_name = socket.gethostname()
host_ip = '0.0.0.0'#  socket.gethostbyname(host_name)
print(host_ip)
port = 9001

def audio_stream():
    s = socket.socket()
    s.bind((host_ip, (port-1)))

    s.listen(5)
    CHUNK = 1024
    # wf = wave.open("temp.wav", 'rb')

    p = pyaudio.PyAudio()
    print('server listening at',(host_ip, (port-1)))
   
    
    stream = p.open(format=pyaudio.paInt16,
                    channels=2,
                    rate=44100,
                    input=True,
                    frames_per_buffer=CHUNK)

             

    conn,addr = s.accept()
 
    data = None
    while True:
        if conn:
            try:
                while True:
                    data = stream.read(CHUNK)
                    # data = wf.readframes(CHUNK)
                    a = pickle.dumps(data)
                    message = struct.pack("Q",len(a))+a
                    conn.sendall(message)
            except:
                print("connection was lost by: ",addr[0])
                break
                

t1 = threading.Thread(target=audio_stream, args=())
t1.start()

