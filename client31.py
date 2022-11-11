import socket,os
import threading, wave, pyaudio, pickle,struct
import numpy as np

host_name = socket.gethostname()
# host_ip="64.44.97.254"
host_ip = '192.168.1.40'
port = 9001
CHUNK = 1024
rate = 44100
buffer = []
recording = True
format = pyaudio.paInt16
p = pyaudio.PyAudio()

stream = p.open(format=format,
    channels=2,
    rate=rate,
    output=True,
    frames_per_buffer=CHUNK)

def start_streaming(): 
    global stream
    stream = p.open(format=format,
        channels=2,
        rate=rate,
        output=True,
        frames_per_buffer=CHUNK)
    print("start recording")
    while recording:
        data = stream.read(CHUNK)
        # data = set_volume(data,1500)
        buffer.append(data)

def set_volume(data, volume):
    # Change value of list of audio chunks
    sound_level = (volume / 100.)
    chunk = np.fromstring(data, np.int16)
    chunk = chunk * sound_level
    data = chunk.astype(np.int16)
    return data

def stop_streaming(stream):
    stream.stop_stream()
    stream.close()
    p.terminate()

def save_file():
    data = wave.open("output.wav","wb")
    data.setnchannels(2)
    data.setsampwidth(p.get_sample_size(format))
    data.setframerate(rate)
    data.writeframes(b"".join(buffer))
    data.close()

def create_socket():
    global s
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        print("Socket creation error: ", str(msg))
    return s

def bind_socket():
    try:
        global s
        print("Binding to port: ",str(port))
        s.bind((host_ip,port))
        s.listen(3)
    except socket.error as msg:
        print("Socket creation error: ", str(msg), "\n" , "Retrying...")
        bind_socket()



def audio_recieve(s):
    stream = p.open(format=format,
    channels=2,
    rate=rate,
    output=True,
    frames_per_buffer=CHUNK)

    # global stream
    # global s
    # create_socket()
    # bind_socket
    print('server listening at ',port)
    # s.connect((host_ip,port))
    print("CLIENT CONNECTED TO ",host_ip)
    while True:
        stream.write(s.recv(CHUNK))


    # data = b""
    # payload_size = struct.calcsize("Q")
    # while True:
    #     try:
    #         while len(data) < payload_size:
    #             packet = s.recv(4*1024) # 4K
    #             if not packet: break
    #             data+=packet
    #         packed_msg_size = data[:payload_size]
    #         data = data[payload_size:]
    #         msg_size = struct.unpack("Q",packed_msg_size)[0]
    #         while len(data) < msg_size:
    #             data += s.recv(4*1024)
    #         frame_data = data[:msg_size]
    #         data  = data[msg_size:]
    #         frame = pickle.loads(frame_data)
    #         stream.write(frame)
    #     except:
    #         break
    # s.close()
    # print("Audio Closed")
    # os._exit(1)



def audio_send(s):

    stream = p.open(format=pyaudio.paInt16,
                channels=2,
                rate=44100,
                input=True,
                frames_per_buffer=CHUNK)

    data = None
    while True:
        if s:
            data = stream.read(CHUNK)
            # data = set_volume(data,1500)
            # a = pickle.dumps(data)
            # message = struct.pack("Q",len(a))+a
            s.sendall(data)
    
def main():
    s = create_socket()
    s.connect((host_ip,port))     
               
    t1 = threading.Thread(target=audio_send, args=(s))
    t2 = threading.Thread(target=audio_recieve, args=(s))
        
    t1.start()
    t2.start()