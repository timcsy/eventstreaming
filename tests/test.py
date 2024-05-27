from eventstreaming import stream
# from eventstreaming.websocket import stream
import time

stream.start(screen=True, fullscreen=True)

state = 0

for i in range(1000):
    time.sleep(0.01)

    frame = stream.get_video_frame()
    if frame is not None:
        print(i, time.time())
        frame['image'].save(f'imgs/{int(1000 * time.time())}.jpg')
    
    # input = stream.get_io_event()
    # if input is not None:
    #     event = input['event']
    #     if event[0] == 'p':
    #         if state == 0:
    #             state = 1
    #     if event[0] == 'r':
    #         if state == 1:
    #             state = 2
    #     if state == 2:
    #         stream.send_io_event(f'p space')
    #         stream.send_io_event(f'r space')
    #         state = 0

stream.close()