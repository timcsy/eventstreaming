import http.server
import socketserver
import asyncio
import concurrent.futures
import os

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Define the allowed files
ALLOWED_FILES = { '', 'index.html', 'index.js' }

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Extract the file name from the request path
        requested_file = self.path.lstrip('/')
        
        # Check if the requested file is allowed
        if requested_file in ALLOWED_FILES:
            super().do_GET()  # Serve the allowed file using the parent class method
        else:
            # If the requested file is not allowed, return 404 Not Found
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

def serve_forever(port=8766):
    # Create and start the TCP server
    with socketserver.TCPServer(("", port), CustomHandler) as httpd:
        print(f"Setup video streaming at http://localhost:{port}")
        httpd.serve_forever()

async def main(port=8766):
    if port is not None:
        # Use ThreadPoolExecutor to run the blocking function in a separate thread
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, serve_forever, (port))

if __name__ == "__main__":
    asyncio.run(main())