import socket
import threading
import pyaudio

class LaunchServer:

    def __init__(self, host, port, slots=8,frame_chunk=4096):
        self.__host = host
        self.__port = port

        self.__slots = slots
        self.__used_slots = 0

        self.__frame_chunk = frame_chunk


        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.bind((self.__host, self.__port))

        self.__block = threading.Lock()
        self.__running = False

        self.users = []

    def start_server(self):
        if self.__running:
            print("Audio server is running already")
        else:
            self.__running = True
            thread = threading.Thread(target=self.__server_listening)
            thread.start()

    def __server_listening(self):
        self.__server_socket.listen()
        while self.__running:
            self.__block.acquire()
            connection, address = self.__server_socket.accept()
            self.users.append((connection, address))
            print(f"Client {connection} Have Been Connected!")
            if self.__used_slots >= self.__slots:
                print("Connection refused! No free slots!")
                connection.close()
                self.__block.release()
                continue
            else:
                self.__used_slots += 1

            self.__block.release()
            thread = threading.Thread(target=self.__client_connection, args=(connection, address,))
            thread.start()

    def __client_connection(self, connection, address):
        while self.__running:
            data = connection.recv(self.__frame_chunk)
            for client in self.users:
                if client[0] != connection:
                    self.__server_socket.send(data)
      
                # try:
                #     if client[0] != connection:
                #         self.__server_socket.send(data)
                # except:
                #     print(f"Client {client[1]} Disconnected!")
                #     client[0].close()
                #     self.users.remove(client)


    # def stop_server(self):
    #     if self.__running:
    #         self.__running = False
    #         closing_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         closing_connection.connect((self.__host, self.__port))
    #         closing_connection.close()
    #         self.__block.acquire()
    #         self.__server_socket.close()
    #         self.__block.release()
    #     else:
    #         print("Server not running!")



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


