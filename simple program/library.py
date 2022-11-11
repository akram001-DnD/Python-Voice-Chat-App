import socket
import threading
import pyaudio
import struct 
import pickle 

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
            print(f"Client {address[0]} Have Been Connected!")
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
            # a = pickle.dumps(data)
            # message = struct.pack("Q",len(a))+a
            for client in self.users:
                if client[0] != connection:
                    client[0].send(data)
                # if client[0] != connection:
                #     client[0].send(data)
                # else:
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
            thread1 = threading.Thread(target=self.__hearing)
            thread2 = threading.Thread(target=self.__recording)

            thread1.start()
            thread2.start()

    def stop_stream(self):
        if self.__running:
            self.__running = False
        else:
            print("Client not streaming")

    def __hearing(self):
        self.__sending_socket.connect((self.__host, self.__port))
        self.__stream = self.__audio.open(format=self.__audio_format, channels=self.__channels, rate=self.__rate, input=True, frames_per_buffer=self.__frame_chunk)
        data_recv = b""
        payload_size = struct.calcsize("Q")
        while self.__running:
            # self.__sending_socket.send(self.__stream.read(self.__frame_chunk))
            try:
                while len(data_recv) < payload_size:
                    packet = self.__sending_socket.recv(self.__frame_chunk) # 4K
                    if not packet: break
                    data_recv+=packet
                packed_msg_size = data_recv[:payload_size]
                data_recv = data_recv[payload_size:]
                msg_size = struct.unpack("Q",packed_msg_size)[0]    
                while len(data_recv) < msg_size:
                    data_recv += self.__sending_socket.recv(self.__frame_chunk)
                frame_data = data_recv[:msg_size]
                data_recv  = data_recv[msg_size:]
                frame = pickle.loads(frame_data)
                self.__stream.write(frame)
            except:
                break

    def __recording(self):
        self.__stream = self.__audio.open(format=self.__audio_format, channels=self.__channels, rate=self.__rate, input=True, frames_per_buffer=self.__frame_chunk)
        while self.__running:
                    data_sent = self.__stream.read(self.__frame_chunk)
                    a = pickle.dumps(data_sent)
                    voice = struct.pack("Q",len(a))+a
                    self.__sending_socket.sendall(voice)

    # def set_volume(self,datalist, volume):
    #     # Change value of list of audio chunks
    #     sound_level = (volume / 100.)
    #     for i in range(len(datalist)):
    #         chunk = np.fromstring(datalist[i], np.int16)
    #         chunk = chunk * sound_level
    #         datalist[i] = chunk.astype(np.int16)


