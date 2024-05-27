import time

# import pyscreenshot as ImageGrab
# for i in range(1000):
#     # img = ImageGrab.grab(backend='mss')
#     # img = ImageGrab.grab()
#     img = ImageGrab.grab(backend='mac_screencapture')
#     print(i)

# from eventstreaming import stream
# stream.start()
# i = 0
# while i < 1000:
#     frames = stream.get_frames()
#     if len(frames) > 0:
#         i += len(frames)
#         print(i)
# stream.close()

import mss
from PIL import Image
with mss.mss() as sct:
    # 获取所有显示器的信息
    monitors = sct.monitors
    # 获取第一个显示器的信息
    monitor = monitors[1]
    print(monitor)
    for i in range(1000):
        # 捕获整个显示器
        # screenshot = sct.grab(monitor)
        screenshot = sct.grab({'left': 0, 'top': 180, 'width': 1440, 'height': 360})
        # 将截图转换为Pillow图像
        img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
        # 调整图像大小
        # img_resized = img.resize((144, 36))
        # 保存截图到文件
        print(i, img.size, time.time())

# from PIL import ImageGrab
# for i in range(1000):
#     ImageGrab.grab()
#     print(i)