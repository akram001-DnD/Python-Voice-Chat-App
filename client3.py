import socket,os
import threading, wave, pyaudio, pickle,struct


host_name = socket.gethostname()
host_ip = '192.168.1.40'#  socket.gethostbyname(host_name)
port = 9001
CHUNK = 1024
rate = 44100
buffer = []
recording = True
format = pyaudio.paInt16
p = pyaudio.PyAudio()

def start_streaming(): 
    stream = p.open(format=format,
        channels=2,
        rate=rate,
        output=True,
        frames_per_buffer=CHUNK)
    print("start recording")
    while recording:
        data = stream.read(CHUNK)
        buffer.append(data)


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
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        print("Socket creation error: ", str(msg))

def bind_socket():
    try:
        global s
        print("Binding to port: ",str(port))
        s.bind((host,port))
        s.listen(3)
    except socket.error as msg:
        print("Socket creation error: ", str(msg), "\n" , "Retrying...")
        bind_socket()

stream = p.open(format=p.get_format_from_width(2),
					channels=2,
					rate=44100,
					output=True,
					frames_per_buffer=CHUNK)        
def audio_stream():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        print("Socket creation error: ", str(msg))
    socket_address = (host_ip,port)
    print('server listening at',socket_address)
    s.connect(socket_address) 
    print("CLIENT CONNECTED TO",socket_address)
    data = b""
    payload_size = struct.calcsize("Q")
    while True:
        try:
            while len(data) < payload_size:
                packet = s.recv(4*1024) # 4K
                if not packet: break
                data+=packet
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("Q",packed_msg_size)[0]
            while len(data) < msg_size:
                data += s.recv(4*1024)
            frame_data = data[:msg_size]
            data  = data[msg_size:]
            frame = pickle.loads(frame_data)
            stream.write(frame)
        except:
            break
    s.close()
    print("Audio Closed")
    os._exit(1)

	
t1 = threading.Thread(target=audio_stream, args=())
t1.start()