import binascii
import asyncio
import json
import zlib
import websockets
import pyaudio
import pickle
import numpy as np
# the AssemblyAI endpoint we're going to hit

URL = "ws://127.0.0.1:4700"
# URL ="ws://echo.websocket.events/"
# python client.py
FRAMES_PER_BUFFER = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
p = pyaudio.PyAudio()

# starts recording

record = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=FRAMES_PER_BUFFER,
)
hear = p.open(format=FORMAT,
    channels=1,
    rate=RATE,
    output=True,
    frames_per_buffer=FRAMES_PER_BUFFER)
def set_volume(data, volume):
        chunk = np.frombuffer(data, dtype = np.int16)
        chunk = chunk * volume
        data = chunk.astype(np.int16)
        data = data.tobytes()      # Activate this for recieved audio
        return data


async def client():
    async with websockets.connect(URL)as ws:
            while True:
                voice = record.read(FRAMES_PER_BUFFER)
                compressed_voice = zlib.compress(voice, 2)
                
                #data = base64.b64encode(data).decode("utf-8")
                #json_data = json.dumps({"audio_data": str(compressed_voice)})
                # json_data = json.dumps({"compressed_voice":str(voice)})

                length = len(compressed_voice)
                print(f'Compressed voice is = {length}.')
                
                
                try:
                    await ws.send(compressed_voice)
                    result =  await ws.recv()
                except websockets.ConnectionClosedError:
                    print("Server Shutted Down")
                

                #audio = bytes(result, 'utf-8') unhexlify
                #audio2 = bytes(result, 'ascii')
                decompressed_voice = zlib.decompress(result)
                decompressed_voice = set_volume(decompressed_voice,3)
                hear.write(decompressed_voice)
                #print("Received '%s'" % result)
                #ws.close()
    
    
asyncio.run(client())