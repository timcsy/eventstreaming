from tkinter import *

root=Tk()
root.withdraw()
#窗體置頂
root.wm_attributes('-topmost',1)
# img=PhotoImage(file='1.png')
# #圖片Label初始設定
# lab1=Label(root,image=img,bd=0)
# lab1.place(x=0,y=0)

#文字Label初始設定
lab2=Label(root,text='顯示文字',bd=0,bg='#FFFAFA')
lab2.place(x=100,y=0)

#root初始設定:視窗無標題欄
root.overrideredirect(True)
#root初始設定:白色為透明色
root.update()
root.geometry('200x300+100+400')
root.configure(bg='#FFFFFF')
root.wm_deiconify()
root.mainloop()
