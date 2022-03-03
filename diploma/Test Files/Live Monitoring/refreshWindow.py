from tkinter import *
import random


SIM_TIME = 30000
global stat

root = Tk()

lab = Label(root)
lab.pack()
dt = 1000  # 1000 ms = 1 s

foo = ['green', 'blue', 'yellow', 'orange']


def getStatus(status):
    # status = random.choice(foo)

    return status


def update():
    lab['bg'] = random.choice(foo)
    root.after(dt, update)  # run itself again after 1000 ms


# run first time
root.after(0, update)

root.after(SIM_TIME, root.destroy)
root.mainloop()
