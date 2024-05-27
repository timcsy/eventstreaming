import threading
import time
from pynput import mouse, keyboard
from pynput.mouse import Button
from pynput.keyboard import Key
from eventstreaming import stream

start_time = 0
io_thread = None
mouse_controller = mouse.Controller()
keyboard_controller = keyboard.Controller()
counters = {} # store the number has been received
terminate = False

def handle_output(event):
    global counters, start_time
    if not event in counters:
        counters[event] = 0
    if counters[event] == 0:
        if not terminate:
            stream.add_input_event({
                'event': event,
                'timestamp': int((time.time() - start_time) * 1_000_000)
            })
    else:
        counters[event] -= 1

def on_move(x, y):
    handle_output(f'm{int(x)},{int(y)}')

def on_click(x, y, button, pressed):
    action = 'p' if pressed else 'r'
    name = f'{button}'[7:]
    on_move(x, y)
    handle_output(f'c{action}{name}')

def on_scroll(x, y, dx, dy):
    on_move(x, y)
    handle_output(f's{int(dx)},{int(dy)}')

def on_press(key):
    try:
        name = f'{key.char}'
        handle_output(f'p{name}')
    except AttributeError:
        name = f'{key}'[4:]
        handle_output(f'p {name}')

def on_release(key):
    try:
        name = f'{key.char}'
        handle_output(f'r{name}')
    except AttributeError:
        name = f'{key}'[4:]
        handle_output(f'r {name}')

def handle_input(event):
    global counters, mouse_controller, keyboard_controller
    if event[0] =='p' or event[0] == 'r' or event[0] == 'm' or event[0] =='c' or event[0] == 's':
        if not event in counters:
            counters[event] = 0
        counters[event] += 1
    if event[0] == 'p':
        if event[1] == ' ': # press char
            keyboard_controller.press(getattr(Key, event[2:]))
        else: # press special
            keyboard_controller.press(event[1])
    if event[0] == 'r':
        if event[1] == ' ': # release char
            keyboard_controller.release(getattr(Key, event[2:]))
        else: # release special
            keyboard_controller.release(event[1])
    if event[0] == 'm': # move absolutely
        x, y = event[1:].split(',')
        mouse_controller.position = (int(x), int(y))
    if event[0] == 'c': # mouse click
        if event[1] == 'p': # mouse press
            mouse_controller.press(getattr(Button, event[2:]))
        elif event[1] == 'r': # mouse release
            mouse_controller.release(getattr(Button, event[2:]))
    if event[0] =='s': # scroll
        dx, dy = event[1:].split(',')
        mouse_controller.scroll(int(dx), int(dy))

def main():
    mouse_listener = mouse.Listener(
        on_move=on_move,
        on_click=on_click,
        on_scroll=on_scroll
    )
    mouse_listener.start()
    keyboard_listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release
    )
    keyboard_listener.start()

def start():
    global start_time, io_thread, terminate
    start_time = time.time()
    terminate = False
    io_thread = threading.Thread(target=main, daemon=True)
    io_thread.start()

def close():
    global io_thread, terminate
    terminate = True
    if io_thread is not None:
        io_thread.join()
        io_thread = None

if __name__ == "__main__":
    start()