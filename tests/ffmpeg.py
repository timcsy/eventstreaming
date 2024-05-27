import asyncio
import subprocess
import websockets

# FFmpeg command: Screen capture using VP9 encoding and output to WebM container
ffmpeg_command = [
    'ffmpeg',
    '-f', 'avfoundation',      # macOS screen capture (Windows would use `gdigrab`)
    '-i', '2',                 # Capture the entire desktop
    '-c:v', 'libvpx-vp9',      # Use VP9 codec
    '-b:v', '2M',              # Set video bitrate to 2 Mbps
    '-f', 'webm',              # Output format as WebM
    'pipe:1'                   # Output to stdout
]

# Frame type mappings
FRAME_TYPE = {
    0: "key frame",
    1: "inter frame (delta)",
    2: "intra-only frame",
    3: "switch frame"
}

async def video_stream(websocket, path):
    """WebSocket server function to receive video frames and send to clients"""
    # Start the FFmpeg process
    process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    buffer = bytearray()  # Buffer for accumulating video frames
    delimiter = b'\x1A\x45\xDF\xA3'  # WebM EBML header delimiter

    try:
        while True:
            chunk = process.stdout.read(4096)  # Read a larger chunk
            if not chunk:
                break
            buffer.extend(chunk)  # Add the data to the buffer

            # Continue finding WebM frames
            while True:
                start = buffer.find(delimiter)  # Find the WebM header
                if start == -1 or len(buffer) < start + 8:
                    break  # No complete frame yet

                frame_length = get_next_frame_length(buffer, start)
                if frame_length is None or len(buffer) < frame_length:
                    break  # Not enough data for a complete frame

                # Extract and identify the frame
                frame = buffer[:frame_length]
                frame_type = detect_frame_type(frame)
                del buffer[:frame_length]

                # Print the frame type
                print(f"Detected frame type: {FRAME_TYPE.get(frame_type, 'unknown')}")

                # Send the complete frame to the WebSocket client
                # await websocket.send(frame)
    finally:
        process.terminate()

def get_next_frame_length(buffer, start):
    """Determine the length of the next frame in the buffer"""
    # Assuming the length is encoded in a fixed field after the delimiter
    if len(buffer) < start + 12:
        return None

    # Example of reading a fixed-length integer field
    length_field_start = start + 8
    length_field_end = start + 12
    length_bytes = buffer[length_field_start:length_field_end]
    frame_length = int.from_bytes(length_bytes, byteorder='big', signed=False)

    return start + frame_length

def detect_frame_type(frame):
    """Detect the frame type from the VP9 bitstream"""
    # Assume the frame type is encoded in the first byte
    if len(frame) < 1:
        return None

    first_byte = frame[0]
    frame_type = (first_byte >> 0) & 0b11  # Assuming type info is in the first byte

    return frame_type

# Start WebSocket server
async def main():
    await video_stream(None, None)

asyncio.run(main())