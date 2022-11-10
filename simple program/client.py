from vidstream import AudioSender
from vidstream import AudioReceiver
import threading 
import socket
#"64.44.97.254"
ip = socket.gethostbyname(socket.gethostname())

receiver = AudioReceiver(ip,9999)
receive_thread = threading.Thread(target = receiver.start_server)

sender = AudioSender("192.168.1.38",9999)
sender_thread = threading.Thread(target = sender.start_stream)

receive_thread.start()
sender_thread.start()



