from library import LaunchServer
from library import LaunchClient
import threading 
import socket
#"64.44.97.254"
recepients = []

client = LaunchClient("192.168.1.40",9999)
client_thread = threading.Thread(target = client.start_stream)
client_thread.start()

# server = LaunchServer("",9999)
# server_thread = threading.Thread(target = server.start_server)
# server_thread.start()
