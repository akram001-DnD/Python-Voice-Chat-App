from library import LaunchServer
from library import LaunchClient
import threading 
import socket
#"64.44.97.254"
recepients = []

# client = LaunchClient("192.168.1.38",9999)
# client_thread = threading.Thread(target = client.start_server)
# client_thread.start()

server = LaunchServer("",9999)
server_thread = threading.Thread(target = server.start_stream)
server_thread.start()
