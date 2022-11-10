from vidstream import AudioSender
from vidstream import AudioReceiver
import threading 
import socket
#"64.44.97.254"
ip = socket.gethostbyname(socket.gethostname())

receiver = AudioReceiver(ip,9999)
receive_thread = threading.Thread(target = receiver.start_server)

sender = AudioSender("64.44.97.254",5554)
sender_thread = threading.Thread(target = sender.start_stream)

receive_thread.start()
sender_thread.start()




from vidstream import StreamingServer

server = StreamingServer('127.0.0.1', 9999)
server.start_server()

# Other Code

# When You Are Done
server.stop_server()