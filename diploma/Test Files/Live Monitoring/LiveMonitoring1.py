import random
from tkinter import *
from enum import Enum


class Status(Enum):
    GREEN = "green"
    ORANGE = "orange"
    RED = "red"


dt = 1000


def live_monitoring():
    # yield
    global depall_status, pasteur_status, filler_status
    window = Tk()

    window.title("Live Process Monitoring!")
    window.geometry('1400x600')

    # Depall
    l1 = Label(bg='green', bd=4, height=7, justify=LEFT, padx=100, relief=RAISED, text='Depall',
               font="Arial 15 bold ")
    l1.grid(row=1, column=0, padx=100, sticky=W)

    # Filler
    l2 = Label(bg='green', bd=4, height=7, justify=CENTER, padx=100, relief=RAISED, text='Filler',
               font="Arial 15 bold ")
    l2.grid(row=1, column=1, padx=100, pady=30, sticky=N)

    # Pasteur
    l3 = Label(bg='green', bd=4, height=7, justify=LEFT, padx=100, relief=RAISED, text='Pasteur',
               font="Arial 15 bold ")
    l3.grid(row=1, column=2, padx=100, sticky=E)

    # Current Process Time
    # pt = Label(bg='#DCDCDC', bd=4, height=2, justify=CENTER, relief=SUNKEN,
    #          text='Current Process Time: ' + str(env.now) + '  minutes', font="Arial 13 bold ")
    # pt.grid(row=2, column=1, pady=70)
    foo = ['green', 'blue', 'yellow', 'orange']

    # Update
    def update():
        l1['bg'] = random.choice(foo)
        l2['bg'] = random.choice(foo)
        l3['bg'] = random.choice(foo)
        # pt['text'] = 'Current Process Time: ' + str(env.now) + '  minutes'
        window.after(1000, update)  # in ms

    update()

    # Close Button
    Button(window, text="Close Live Monitoring", height=2, width=10, font="Arial 12 bold ", justify=CENTER, bd='5',
           bg='#479997',
           command=window.destroy).grid(row=4, column=1, pady=70)
    # print(window.state)
    window.mainloop()


# Test Code
lis = [Status.GREEN, Status.ORANGE, Status.RED]
live_monitoring()
