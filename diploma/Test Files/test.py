import random
from tkinter import *
from functools import partial
from PIL import ImageTk, Image

dt = 1000
count = 3
duration = '2h 22min'
capacity = 3000
pc_time = 10
# Odd number = machines (1,3,5..)
# Even number = conveyors (0,2,4,6..)


def machine_details_window(machine_name):
    """ Machine Details """

    root = Tk()
    window_colour = '#AADCD9'
    root.title("Machine Details")
    root.configure(bg=window_colour)
    root.geometry('1900x900')

    # Title
    Label(root, bg="light blue", relief=GROOVE, text="MACHINE DETAILS", font="Arial 25 bold").grid(row=0, column=2, pady=5)

    def to_do(m_name, level_cans):

        # Name
        Label(root, bg='#8DCDBA', bd=4, relief=RAISED, text=m_name, font="Arial 15 bold").grid(row=3, column=1, padx=100, sticky=W)

        # Cans Level
        Label(root, bg='white', padx=30, relief=RIDGE, text=level_cans, font="Arial 15 bold").grid(row=7, column=1, sticky=W, padx=150)
        # Duration
        Label(root, bg='white', padx=30, relief=RIDGE, text=duration, font="Arial 15 bold").grid(row=8, column=1, sticky=W, padx=150)
        # Current Process Time
        pt_c = Label(root, bg='#BFFCBC', bd=4, height=2, justify=CENTER, relief=RAISED, text='Current Cans Level: ' + str(level_cans) + '  cans', font="Arial 13 bold ")
        return pt_c

    if machine_name == 'DEPALL':
        PT_C = to_do(machine_name, 123093)
    elif machine_name == 'FILLER':
        to_do(machine_name, 3123493)
    elif machine_name == 'PASTEUR':
        to_do(machine_name, 12345)
    '''
    # Update
    def update_fun():
        PT_C['text'] = 'Current Process Time: ' + str(dt) + '  seconds'
        root.after(dt, update_fun)

    print(root.state())
    if root.state() == 'normal':
        print('running !!')
        update_fun()
    '''

    Button(root, text="Close", height=2, width=10, font="Arial 12 bold ", justify=CENTER, bd='5', bg='#479997', command=root.destroy).grid(row=9, column=2, pady=70)
    print(root.state())
    root.resizable(True, True)
    root.mainloop()


def live_monitoring():
    """Live Simulation Monitoring"""

    window = Tk()
    window_colour = '#D6EBFE'
    window.title("Live Process Monitoring!")
    window.configure(bg=window_colour)
    window.geometry('1900x1200')

    Label(window, bg=window_colour).grid(row=10, column=4)

    # Title
    Label(window, bg="light blue",  relief=GROOVE, text="LIVE PROCESS SIMULATION", font="Arial 25 bold").grid(row=0, sticky='EW', pady=5, columnspan=10)
    # KPIs Title
    Label(window, bg="#C1FBF1", relief=GROOVE, text="KPIs - Root Cause Analysis", font="Arial 25 bold").grid(row=7, sticky='EW', pady=10, columnspan=10)
    # Run
    Label(window, bg='#878787', relief=GROOVE, text='RUN:', font="Arial 15 bold", fg='#95F920').grid(row=10, column=0, pady=5)
    # Stand By
    Label(window, bg='#878787', relief=GROOVE, text='STAND BY:', font="Arial 15 bold", fg='#E3E132').grid(row=11, column=0, pady=5)
    # Stop
    Label(window, bg='#878787', relief=GROOVE, text='STOP:', font="Arial 15 bold", fg='#BE0000').grid(row=12, column=0, pady=5)

    # Current Process Time
    pt = Label(window, bg='#BFFCBC', bd=4, height=2, justify=CENTER, relief=RAISED, text='Current Process Time: ' + str(pc_time) + '  seconds', font="Arial 13 bold ")
    pt.grid(row=6, pady=25, columnspan=20)

    # Image Depall
    # imgD = ImageTk.PhotoImage(Image.open("images\\depall.png").resize((350, 260)))
    # Label(window, image=imgD, bd=4, width=350, height=260, relief=RAISED).grid(row=4, column=1, padx=0)
    # Image Filler
    # imgF = ImageTk.PhotoImage(Image.open("images\\filler.png").resize((350, 260)))
    # Label(window, image=imgF, bd=4, width=350, height=260, relief=RAISED).grid(row=4, column=3, padx=0)
    # Image Pasteur
    # imgP = ImageTk.PhotoImage(Image.open("images\\pasteur.png").resize((350, 260)))
    # Label(window, image=imgP, bd=4, width=350, height=260, relief=RAISED).grid(row=4, column=5, padx=0)

    def machine_object(col, machine_name):
        # Φάρος
        LB3 = Label(window, bg='#FAB3B3', bd=4, width=3, height=2, relief=RAISED)
        LB3.grid(row=1, column=col, sticky=W)
        LB2 = Label(window, bg='#FBF3C1', bd=4, width=3, height=2, relief=RAISED)
        LB2.grid(row=2, column=col, sticky=W)
        LB1 = Label(window, bg='#D9F2CC', bd=4, width=3, height=2, relief=RAISED)
        LB1.grid(row=3, column=col, sticky=W)
        # Name
        Button(window, bg='#8DCDBA', bd=4, relief=RAISED, text=machine_name, font="Arial 13 bold", command=partial(machine_details_window, machine_name)).grid(row=3, column=col, padx=80, sticky=W)

        return LB3, LB2, LB1

    def current_conveyor_capacity_buffer(col, current_level, machine_capacity):
        """ Current level capacity status of conveyors """
        Label(window, text=str(current_level) + ' / ' + str(machine_capacity), relief=RIDGE, font="Arial 15 bold").grid(row=5, column=col, pady=10, ipadx=5, ipady=15)

    def current_machine_buffer(col, current_level, machine_capacity):
        Label(window, text=str(current_level) + ' / ' + str(machine_capacity), relief=RIDGE, font="Arial 15 bold").grid(row=5, column=col, pady=10, ipadx=125, ipady=15)

    def kpis(col, count_standby, duration_standby, count_stop, duration_stop):
        # Label
        Label(window, bg=window_colour, text='COUNT', font="Arial 15 bold").grid(row=9, column=col, sticky=W)
        Label(window, bg=window_colour, text='DURATION', font="Arial 15 bold").grid(row=9, column=col, sticky=E)
        # Run
        Label(window, bg='#9FE849', padx=30, relief=RIDGE, text=count_standby, font="Arial 15 bold").grid(row=10, column=col, sticky=W)
        Label(window, bg='#9FE849', padx=30, relief=RIDGE, text=duration_standby, font="Arial 15 bold").grid(row=10, column=col, sticky=E)
        # Stand By
        Label(window, bg='#F5F372', padx=30, relief=RIDGE, text=count_standby, font="Arial 15 bold").grid(row=11, column=col, sticky=W)
        Label(window, bg='#F5F372', padx=30, relief=RIDGE, text=duration_standby, font="Arial 15 bold").grid(row=11, column=col, sticky=E)
        # Stop
        Label(window, bg='#F57272', padx=30, relief=RIDGE, text=count_stop, font="Arial 15 bold").grid(row=12, column=col, sticky=W)
        Label(window, bg='#F57272', padx=30, relief=RIDGE, text=duration_stop, font="Arial 15 bold").grid(row=12, column=col, sticky=E)

    # Raw Material
    current_conveyor_capacity_buffer(0, 500, 5000)

    # Depall
    D_BL3, D_BL2, D_BL1 = machine_object(1, 'DEPALL')
    current_machine_buffer(1, 1000, 3000)
    kpis(1, '4', '2h 21min', '3', '6h 30min')
    # Depall - Filler conveyor
    current_conveyor_capacity_buffer(2, 500, 5000)
    # Filler
    F_BL3, F_BL2, F_BL1 = machine_object(3, 'FILLER')
    current_machine_buffer(3, 100, 200)
    kpis(3, '20', '9h 21min', '5', '21h 30min')
    # Filler - Pasteur conveyor
    current_conveyor_capacity_buffer(4, 500, 5000)
    # Pasteur
    P_BL3, P_BL2, P_BL1 = machine_object(5, 'PASTEUR')
    current_machine_buffer(5, 10000, 20000)
    kpis(5, '5', '6h 21min', '12', '9h 30min')
    # Pasteur - _  conveyor
    current_conveyor_capacity_buffer(6, 500, 5000)

    ll3 = ['red', '#FAB3B3']
    ll2 = ['yellow', '#FFEFAA']
    ll1 = ['green', '#D9F2CC']

    # Update
    def update():
        D_BL1['bg'] = 'green'
        F_BL2['bg'] = 'yellow'

        P_BL3['bg'] = random.choice(ll3)
        P_BL2['bg'] = random.choice(ll2)
        P_BL1['bg'] = random.choice(ll1)
        pt['text'] = 'Current Process Time: ' + str(dt) + '  seconds'
        window.after(dt, update)

    update()

    # Close Button
    Button(window, text="Close", height=2, width=10, font="Arial 12 bold ", justify=CENTER, bd='5', bg='#479997',
           command=window.destroy).grid(row=15, columnspan=10, pady=40)

    window.resizable(True, True)
    window.mainloop()


live_monitoring()
