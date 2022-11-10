from vidstream import StreamingServer

server = StreamingServer('0.0.0.0', 9999)
server.start_server()

# Other Code

# When You Are Done
server.stop_server()