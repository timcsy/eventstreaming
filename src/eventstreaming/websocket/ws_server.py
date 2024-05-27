import asyncio
from websockets.server import serve

ws = {
    'video': None,
    'screen': None,
    'input': None,
    'env': None
}

async def ws_server(websocket):
    ws_type = None
    try:
        async for message in websocket:
            if message == 'video' or message == 'screen' or message == 'input' or message == 'env':
                ws_type = message
                ws[ws_type] = websocket
                print(f'The {ws_type} websocket is connected')
            if ws['env'] is not None:
                if ws_type == 'video' or ws_type == 'screen' or ws_type == 'input':
                    await ws['env'].send(message)
            if ws['video'] is not None:
                if ws_type == 'video':
                    await ws['video'].send(message)
            if ws['input'] is not None:
                if ws_type == 'env':
                    await ws['input'].send(message)
    except Exception as e:
        pass
    if ws_type is not None:
        ws[ws_type] = None
        print(f'The {ws_type} websocket is disconnected')
        ws_type = None

async def main():
    async with serve(ws_server, 'localhost', 8765):
        await asyncio.Future()  # run forever

def start():
    asyncio.run(main())

if __name__ == "__main__":
    start()