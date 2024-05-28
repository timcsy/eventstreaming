import threading
import time
import websocket
import av
import sys
import mss
from PIL import ImageGrab
import pyautogui
import numpy as np
import struct

start_time = 0
ws_thread = None
screen_thread = None
terminate = False

def on_open(ws: websocket.WebSocketApp):
    ws.send('screen')

def on_message(ws, message):
    pass

def on_error(ws, error):
    print(f'Screen WebSocket Client Error: {error}')

def on_close(ws, close_status_code, close_msg):
    global terminate
    terminate = True
    # print(f'Connection closed, close status code: {close_status_code}', close_msg)

ws = websocket.WebSocketApp(
    'ws://localhost:8765',
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)

def send_packet(packet):
    global start_time, ws
    timestamp = int((time.time() - start_time) * 1_000_000)
    is_keyframe = packet.is_keyframe
    data = bytes(packet)
    header = struct.pack('<BBBBQI', 0, 0, 0, is_keyframe, timestamp, len(data))
    if not terminate:
        ws.send(header + data, websocket.ABNF.OPCODE_BINARY)

def main(left=None, top=None, width=None, height=None, new_width=None, new_height=None, fullscreen=False):
    if sys.platform == 'win32':
        size = pyautogui.size()

        if fullscreen:
            left = 0
            top = 0
            width = size.width
            height = size.height
        if left is None:
            left = 0
        if top is None:
            top = 0
        if width is None:
            width = size.width
        if height is None:
            height = size.height
        if new_width is None:
            new_width = width
        if new_height is None:
            new_height = height

        codec = av.codec.CodecContext.create('vp9', 'w')
        codec.width = new_width
        codec.height = new_height
        codec.pix_fmt = 'yuv420p'
        codec.bit_rate = 2_000_000
        codec.options = {'profile': '0'}
        
        while not terminate:
            screenshot = ImageGrab.grab(bbox=(left, top, left + width, top + height))
            img = np.array(screenshot)
            frame = av.VideoFrame.from_ndarray(img, format='bgra')
            frame = frame.reformat(width=codec.width, height=codec.height, format='yuv420p')
            for packet in codec.encode(frame):
                send_packet(packet)
            time.sleep(0.001)
        for packet in codec.encode():
            send_packet(packet)
    else:
        with mss.mss() as sct:
            monitors = sct.monitors
            monitor = monitors[1]

            if fullscreen:
                left = monitor['left']
                top = monitor['top']
                width = monitor['width']
                height = monitor['height']
            if left is None:
                left = monitor['left']
            if top is None:
                top = monitor['top']
            if width is None:
                width = monitor['width']
            if height is None:
                height = monitor['height']
            if new_width is None:
                new_width = width
            if new_height is None:
                new_height = height

            codec = av.codec.CodecContext.create('vp9', 'w')
            codec.width = new_width
            codec.height = new_height
            codec.pix_fmt = 'yuv420p'
            codec.bit_rate = 2_000_000
            codec.options = {'profile': '0'}

            while not terminate:
                screenshot = sct.grab({'left': left, 'top': top, 'width': width, 'height': height})
                img = np.array(screenshot)
                frame = av.VideoFrame.from_ndarray(img, format='bgra')
                frame = frame.reformat(width=codec.width, height=codec.height, format='yuv420p')
                for packet in codec.encode(frame):
                    send_packet(packet)
                time.sleep(0.001)
        
        for packet in codec.encode():
            send_packet(packet)

def start(left=None, top=None, width=None, height=None, new_width=None, new_height=None, fullscreen=False):
    global ws, start_time, ws_thread, screen_thread, terminate
    start_time = time.time()
    terminate = False
    ws_thread = threading.Thread(target=ws.run_forever, daemon=True)
    ws_thread.start()
    screen_thread = threading.Thread(target=main, args=(left, top, width, height, new_width, new_height, fullscreen), daemon=True)
    screen_thread.start()

def close():
    global ws, ws_thread, screen_thread, terminate
    terminate = True
    ws.close()
    if ws_thread is not None:
        ws_thread.join()
        ws_thread = None
    if screen_thread is not None:
        screen_thread.join()
        screen_thread = None

if __name__ == "__main__":
    start(fullscreen=True)