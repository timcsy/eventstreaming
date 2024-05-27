import queue
import threading
import time
import websocket
import json
from eventstreaming.websocket import video, screen_recorder, io_event

start_time = 0
ws_thread = None
has_screen = False
terminate = False

MAX_VIDEO_QUEUE_SIZE = 5
video_queue = queue.Queue(maxsize=MAX_VIDEO_QUEUE_SIZE)
input_queue = queue.Queue()

def on_open(ws: websocket.WebSocketApp):
    ws.send('env')

def on_message(ws, message):
    global video_queue, input_queue
    if message[0] == 0:
        imgs = video.decode_rawdata(message)
        for img in imgs:
            if video_queue.full():
                video_queue.get()
            video_queue.put(img)
    elif message[0] == '{':
        input_queue.put(json.loads(message))

def on_error(ws, error):
    print(f'Stream WebSocket Client Error: {error}')

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

def get_video_frame():
    global video_queue
    if video_queue.empty():
        return None
    return video_queue.get_nowait()

def get_io_event():
    global input_queue
    if input_queue.empty():
        return None
    return input_queue.get_nowait()

def get_io_events():
    input_events = []
    event = get_io_event()
    while event is not None:
        input_events.append(event)
        event = get_io_event()
    return input_events

def send_io_event(event):
    ws.send(json.dumps({
        'event': event,
        'timestamp': int((time.time() - start_time) * 1_000_000) 
    }))

def start(waiting_secs=0.5, screen=True, left=None, top=None, width=None, height=None, new_width=None, new_height=None, fullscreen=False):
    global start_time, ws, ws_thread, has_screen, terminate
    start_time = time.time()
    terminate = False
    ws_thread = threading.Thread(target=ws.run_forever, daemon=True)
    ws_thread.start()
    io_event.start()
    has_screen = screen
    if has_screen:
        screen_recorder.start(left=left, top=top, width=width, height=height, new_width=new_width, new_height=new_height, fullscreen=fullscreen)
    time.sleep(waiting_secs) # wait for the connection

def close():
    global ws, ws_thread, has_screen, terminate
    terminate = True
    ws.close()
    if ws_thread is not None:
        ws_thread.join()
        ws_thread = None
    io_event.close()
    if has_screen:
        screen_recorder.close()