import socket
import pyaudio
import threading





class LaunchClient:

    def __init__(self, host, port, audio_format=pyaudio.paInt16, channels=1, rate=44100, frame_chunk=4096):
        self.__host = host
        self.__port = port

        self.__audio_format = audio_format
        self.__channels = channels
        self.__rate = rate
        self.__frame_chunk = frame_chunk

        self.__sending_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__audio = pyaudio.PyAudio()

        self.__running = False

    def start_stream(self):
        if self.__running:
            print("Already streaming")
        else:
            self.__running = True
            thread = threading.Thread(target=self.__client_streaming)
            thread.start()

    def stop_stream(self):
        if self.__running:
            self.__running = False
        else:
            print("Client not streaming")

    def __client_streaming(self):
        self.__sending_socket.connect((self.__host, self.__port))
        self.__stream = self.__audio.open(format=self.__audio_format, channels=self.__channels, rate=self.__rate, input=True, frames_per_buffer=self.__frame_chunk)
        while self.__running:
            self.__sending_socket.send(self.__stream.read(self.__frame_chunk))
            data = self.__sending_socket.recv(self.__frame_chunk)
            self.__stream.write(data)
    
    # def set_volume(self,datalist, volume):
    #     # Change value of list of audio chunks
    #     sound_level = (volume / 100.)
    #     for i in range(len(datalist)):
    #         chunk = np.fromstring(datalist[i], np.int16)
    #         chunk = chunk * sound_level
    #         datalist[i] = chunk.astype(np.int16)




