import asyncio
import sys
from eventstreaming.websocket import ws_server, web_server

async def main(http_port=8766):
    await asyncio.gather(
        ws_server.main(),
        web_server.main(http_port)
    )

def run_main(http_port=None):
    if len(sys.argv) > 1:
        http_port = int(sys.argv[1])
    try:
        asyncio.run(main(http_port))
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    run_main()