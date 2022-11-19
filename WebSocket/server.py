import asyncio
import websockets

connected = set()

async def server(websocket, path):
    connected.add(websocket)
    print(f"Client {websocket} Has connected!")
    try:
        async for message in websocket:
            voice = message
            for conn in connected:
                # if conn != websocket:
                    await conn.send(voice)

    except websockets.ConnectionClosedError:
        print("Client Disconnected.")
    finally:
        conn.close()
        connected.remove(conn)



async def main():
    print(f"server listening ...")
    async with websockets.serve(server, "localhost", 4700):
        await asyncio.Future()  # run forever

asyncio.run(main())

#python server.py

