import json
import queue
import time
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

def get_io_events(timestamp=True):
    input_events = []
    event = get_io_event()
    while event is not None:
        input_events.append(event)
        event = get_io_event()
    if not timestamp:
        return list(map(lambda x: x['event'], input_events))
    return input_events

def send_io_event(event):
    io_event.handle_input(event)

def record_io_event(path=None):
    inputs = []
    tmp_inputs = []
    state = 'start'
    while True:
        input = get_io_event()
        while input is None:
            time.sleep(0.001)
            input = get_io_event()
        if state =='start' and (input['event'] == 'p alt' or input['event'] == 'p alt_l'):
            state = 'alt'
            tmp_inputs.append(input)
        elif state =='alt' and input['event'] == 'pr':
            state = 'end'
            break
        else:
            if state != 'end' and len(tmp_inputs) > 0:
                inputs.extend(tmp_inputs)
                tmp_inputs = []
            state = 'start'
            inputs.append(input)
    if path is None:
        print(inputs)
    else:
        with open(path, 'w') as fout:
            json.dump(inputs, fout, indent=4)

def play_io_event(records=None):
    record_queue = queue.Queue()

    record_list = []
    if type(records) == str:
        with open(records, 'r') as fin:
            record_list = json.load(fin)
    elif type(records) == list:
        record_list = records
    for record in record_list:
        record_queue.put(record)
    
    start_time = time.time()
    record = record_queue.get_nowait()
    while record is not None:
        event_time = record['timestamp'] / 1_000_000.0
        if time.time() >= start_time + event_time:
            send_io_event(record['event'])
            if record_queue.empty():
                record = None
            else:
                record = record_queue.get_nowait()

def start(left=None, top=None, width=None, height=None, new_width=None, new_height=None, fullscreen=False, screen=True, waiting_secs=0.5):
    io_event.start()
    screen_recorder.start(left=left, top=top, width=width, height=height, new_width=new_width, new_height=new_height, fullscreen=fullscreen)

def close():
    io_event.close()
    screen_recorder.close()