import tkinter as tk

def move_window(event):
    x = event.x_root - start_x
    y = event.y_root - start_y
    root.geometry(f'+{x}+{y}')

def start_move(event):
    global start_x, start_y
    start_x = event.x_root - root.winfo_x()
    start_y = event.y_root - root.winfo_y()

root = tk.Tk()
root.withdraw()
root.overrideredirect(True)  # 移除標題欄
root.geometry('300x200')

title_bar = tk.Frame(root, bg='gray', relief='raised', bd=2)
title_bar.pack(side='top', fill='x')

title_bar.bind('<Button-1>', start_move)
title_bar.bind('<B1-Motion>', move_window)

content = tk.Frame(root)
content.pack(expand=True, fill='both')

root.resizable()

root.wm_deiconify()
root.mainloop()
