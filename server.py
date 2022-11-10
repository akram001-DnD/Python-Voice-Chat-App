from time import sleep
from threading import Thread, Lock, Condition
import pickle
import socket

# SOCK_IP = '10.128.0.2'  # internal IP  of the server
SOCK_IP = '192.168.1.40'  # internal IP  of the server
SOCK_PORT = 9001


class Client:
    allClients = []
    availableClients = {}  # {'client sender' : client object}


    def __init__(self, client_ptr):
        Client.allClients.append(self)
        self.cl_ptr = client_ptr
        self.sender = None
        self.sender = self.get_sender()
        self.recipients = None
        self.recipients = self.get_recipients()
        print(f"received sender {self.sender} and recipient {self.recipients}")
        Client.availableClients[self.sender] = self
        try:
            self.lobby()
        except ConnectionResetError:
            print("CONNECTION RESET ERROR")
            self.close()
        except BrokenPipeError:
            print("BROKEN PIPE. Closing connection")
            self.close()

    def lobby(self):
        cl = None
        while True:
            try:
                cl = Client.availableClients[self.recipients]
                if cl.get_recipients() == self.sender:
                    break
                else:
                    print("recipient busy.")
                    sleep(1)
            except KeyError:
                print("waiting...")
                sleep(1)
                continue
        if cl is not None:
            # found a client who wants to connect to self
            self.cl_ptr[0].send('go'.encode())
            self.converse(cl)
        self.close()

    # Enter a loop to keep searching for recipient in available clients

    def get_sender(self):
        if self.sender is None:
            # receive sender
            self.sender = self.cl_ptr[0].recv(512).decode().rstrip()
            print(f"Client connected: {self.sender}")
        return self.sender

    def get_recipients(self):
        if self.recipients is None:
            # receive recipient sender
            self.recipients = self.cl_ptr[0].recv(512).decode().rstrip()
            print(f"Client {self.sender} wants to connect to {self.recipients}")
        return self.recipients

    # def getRecipientSocket(self):
    #     search list of available clients

    def converse(self, recipient_obj):
        print("establishing connection...")
        try:
            while True:
                self.send(recipient_obj, self.read())
        except KeyboardInterrupt:
            self.close()
        except OSError:
            self.close()

    def send(self, cl_object, data):
        cl_object.cl_ptr[0].send(data)

    def read(self):
        return self.cl_ptr[0].recv(1024)

    def close(self):
        try:
            Client.allClients.remove(self)
        except ValueError:
            print("Client does not exist in 'allClients' array")
        Client.availableClients.pop(self.get_sender(), None)
        self.cl_ptr[0].close()
        print(f"Client {self.sender} removed.")

def main():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"binding socket on {SOCK_IP}:{SOCK_PORT}")
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind(("0.0.0.0", SOCK_PORT))
    serversocket.listen(3)

    while True:
        try:
            client_id = (serversocket.accept(),)
            thrd1 = Thread(target=client_handler, args=client_id)
            thrd1.start()
        except KeyboardInterrupt:
            serversocket.close()
            break

def client_handler(clientid):
    Client(clientid)

main()
