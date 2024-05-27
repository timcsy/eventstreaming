import mss
import pygetwindow as gw
# from pywinauto import Desktop

def capture_specific_window(window_title):
    # 获取所有匹配窗口标题的窗口
    windows = gw.getWindowsWithTitle(window_title)
    
    if not windows:
        print(f"No window found with title: {window_title}")
        return
    
    # 获取第一个匹配的窗口
    window = windows[0]
    print(f"Found window: {window.title}")

    # 使用 pywinauto 使窗口可见（如果被遮挡）
    app = Desktop(backend="uia")
    app_window = app.window(title=window_title)
    app_window.restore()  # 确保窗口可见
    app_window.set_focus()  # 将焦点设置到该窗口

    # 获取窗口的位置和大小
    left, top, right, bottom = app_window.rectangle().left, app_window.rectangle().top, app_window.rectangle().right, app_window.rectangle().bottom
    width, height = right - left, bottom - top

    # 使用 mss 截取窗口区域
    with mss.mss() as sct:
        monitor = {"top": top, "left": left, "width": width, "height": height}
        screenshot = sct.grab(monitor)
        mss.tools.to_png(screenshot.rgb, screenshot.size, output='specific_window.png')
    
    print("Screenshot saved as 'specific_window.png'")

if __name__ == "__main__":
    # capture_specific_window("Untitled - Notepad")  # 替换为你要截取的窗口标题
    print(gw.getAllTitles())
    window = gw.getWindowsWithTitle('Google Chrome chrome://dino/')
    print(window.size)