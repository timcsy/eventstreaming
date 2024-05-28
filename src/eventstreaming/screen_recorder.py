import threading
import time
import sys
import mss
from PIL import Image, ImageGrab
import pyautogui
from eventstreaming import stream

start_time = 0
screen_thread = None
terminate = False

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
        
        while not terminate:
            img = ImageGrab.grab(bbox=(left, top, left + width, top + height))
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            timestamp = int((time.time() - start_time) * 1_000_000)
            stream.add_video_frame({
                'image': resized_img,
                'timestamp': timestamp
            })
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

            while not terminate:
                screenshot = sct.grab({'left': left, 'top': top, 'width': width, 'height': height})
                img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                timestamp = int((time.time() - start_time) * 1_000_000)
                stream.add_video_frame({
                    'image': resized_img,
                    'timestamp': timestamp
                })

def start(left=None, top=None, width=None, height=None, new_width=None, new_height=None, fullscreen=False):
    global start_time, screen_thread, terminate
    start_time = time.time()
    terminate = False
    screen_thread = threading.Thread(target=main, args=(left, top, width, height, new_width, new_height, fullscreen), daemon=True)
    screen_thread.start()

def close():
    global screen_thread, terminate
    terminate = True
    if screen_thread is not None:
        screen_thread.join()
        screen_thread = None

if __name__ == "__main__":
    start(fullscreen=True)