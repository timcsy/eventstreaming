from eventstreaming import stream
# from eventstreaming.websocket import stream
import time

stream.start()

# Focus on the game
stream.send_io_event('m200,860')
stream.send_io_event('cpleft')
stream.send_io_event('crleft')
time.sleep(1)
stream.send_io_event('p space')
stream.send_io_event('r space')

for i in range(10000):
    time.sleep(0.01)

    frame = stream.get_video_frame()
    if frame is not None:
        frame['image'].save(f'imgs/{int(time.time() * 1000)}.jpg')
    
    input = stream.get_io_event()
    if input is not None:
        event = input['event']
        if event == 'pw':
            stream.send_io_event(f'p up')
            time.sleep(0.1)
            stream.send_io_event(f'r up')
        elif event == 'ps':
            stream.send_io_event(f'p down')
            time.sleep(0.5)
            stream.send_io_event(f'r down')

stream.close()