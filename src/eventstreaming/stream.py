import queue
from eventstreaming import screen_recorder, io_event

MAX_VIDEO_QUEUE_SIZE = 5
video_queue = queue.Queue(maxsize=MAX_VIDEO_QUEUE_SIZE)
input_queue = queue.Queue()

def add_video_frame(frame):
    # with timestamp
    global video_queue
    if video_queue.full():
        video_queue.get()
    video_queue.put(frame)

def add_input_event(event):
    # with timestamp
    global input_queue
    input_queue.put(event)

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
    io_event.handle_input(event)

def start(left=None, top=None, width=None, height=None, new_width=None, new_height=None, fullscreen=False, screen=True, waiting_secs=0.5):
    io_event.start()
    screen_recorder.start(left=left, top=top, width=width, height=height, new_width=new_width, new_height=new_height, fullscreen=fullscreen)

def close():
    io_event.close()
    screen_recorder.close()