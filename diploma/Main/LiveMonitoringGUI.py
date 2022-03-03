import random
from tkinter import *
from functools import partial
from PIL import ImageTk, Image

dt = 1000
count = 3
duration = '2h 22min'
capacity = 3000
pc_time = 10
stop_dur = 30
MANUAL_BRAKE_VAR = 1


# Odd number = machines (1,3,5..)
# Even number = conveyors (0,2,4,6..)
def t_brakedown(col):
    # Statement
    if col == 1:
        # machine_name = 'Depall'
        print('Button Depall Pressed')
    elif col == 3:
        # machine_name = 'Filler'
        print('Button Filler Pressed')
    elif col == 5:
        # machine_name = 'Pasteur'
        print('Button Pasteur Pressed')


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
        to_do(machine_name, 123093)
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
    window.geometry('1800x1200')

    # Titles
    Label(window, bg="light blue",  relief=GROOVE, text="LIVE PROCESS SIMULATION", font="Arial 25 bold").grid(row=0, sticky='EW', pady=5, columnspan=10)
    # KPIs Title
    Label(window, bg="#C1FBF1", relief=GROOVE, text="Root Cause Analysis - KPIs", font="Arial 25 bold").grid(row=9, sticky='EW', pady=10, columnspan=10)
    # Run Title
    Label(window, bg='#878787', relief=GROOVE, text='RUN:', font="Arial 15 bold", fg='#95F920').grid(row=12, column=0, pady=5, ipadx=35)
    # Stand By Title
    Label(window, bg='#878787', relief=GROOVE, text='STAND BY:', font="Arial 15 bold", fg='#E3E132').grid(row=13, column=0, pady=5, ipadx=7)
    # Stop Title
    Label(window, bg='#878787', relief=GROOVE, text='STOP:', font="Arial 15 bold", fg='#BE0000').grid(row=14, column=0, pady=5, ipadx=30)

    # Current Process Time
    pt = Label(window, bg='#6B8CD3', bd=4, height=2, justify=CENTER, relief=RAISED, text='Current Process Time: ' + str(pc_time) + '  seconds', font="Arial 13 bold ")
    pt.grid(row=8, pady=25, columnspan=20)

    # Image Depall
    imgD = ImageTk.PhotoImage(Image.open("images\\depall.png").resize((350, 260)))
    Label(window, image=imgD, bd=4, width=350, height=260, relief=RAISED).grid(row=4, column=1, padx=20)
    # Image Filler
    imgF = ImageTk.PhotoImage(Image.open("images\\filler.png").resize((350, 260)))
    Label(window, image=imgF, bd=4, width=350, height=260, relief=RAISED).grid(row=4, column=3, padx=20)
    # Image Pasteur
    imgP = ImageTk.PhotoImage(Image.open("images\\pasteur.png").resize((350, 260)))
    Label(window, image=imgP, bd=4, width=350, height=260, relief=RAISED).grid(row=4, column=5, padx=20)

    def machine_beacon(col, machine_name):
        # Beacon
        LB3 = Label(window, bg='#FAB3B3', bd=4, width=3, height=2, relief=RAISED)
        LB3.grid(row=1, column=col, padx=180, sticky=W)
        LB2 = Label(window, bg='#FBF3C1', bd=4, width=3, height=2, relief=RAISED)
        LB2.grid(row=2, column=col, padx=180, sticky=W)
        LB1 = Label(window, bg='#D9F2CC', bd=4, width=3, height=2, relief=RAISED)
        LB1.grid(row=3, column=col, padx=180, sticky=W)
        # Name
        Button(window, bg='#8DCDBA', bd=4, relief=RAISED, text=machine_name, font="Arial 13 bold", command=partial(machine_details_window, machine_name)).grid(row=3, column=col, padx=20, sticky=W)

        return LB3, LB2, LB1

    def current_conveyor_capacity_buffer(col, i_padx, current_level, machine_capacity, machine_description):
        """ Current level capacity status of conveyors """
        Label(window, text=machine_description, font="Arial 13", bg=window_colour, wraplength=140).grid(row=6, column=col, pady=0, sticky=S)
        Label(window, text=str(current_level) + ' / ' + str(machine_capacity), relief=RIDGE, font="Arial 15 bold", justify=CENTER).grid(row=7, column=col, ipadx=i_padx, ipady=15)

    def current_machine_buffer_and_brake(col, i_padx, current_level, machine_capacity, machine_description):
        """ Current machine level capacity"""
        machine_name = ''
        Label(window, text=machine_description, font="Arial 13", bg=window_colour).grid(row=6, column=col, pady=0, sticky=S)
        Label(window, text=str(current_level) + ' / ' + str(machine_capacity), relief=RIDGE, font="Arial 15 bold", justify=CENTER).grid(row=7, column=col, pady=0, ipadx=i_padx, ipady=15)
        # Machine Brake Button
        if MANUAL_BRAKE_VAR == 1:
            # Brake Button
            Button(window, text='BRAKE', command=partial(t_brakedown, col), bg='#D97854', bd=4, font="Arial 13 bold", relief=RAISED, activebackground='#D97854').grid(row=5, column=col, sticky=W, pady=5, padx=100)
            # Repair Button
            Button(window, text='Repair', command=partial(t_brakedown, col), bg='#86D954', bd=4, font="Arial 13 bold", relief=RAISED, activebackground='#86D954').grid(row=5, column=col, sticky=E, pady=5, padx=100)

        return machine_name

    def kpis(col, count_standby, duration_standby, count_stop, duration_stop):
        # Label
        Label(window, bg=window_colour, text='TIMES', font="Arial 15 bold").grid(row=10, column=col, sticky=W, padx=50)
        Label(window, bg=window_colour, text='DURATION', font="Arial 15 bold").grid(row=10, column=col, sticky=E, padx=80)
        # Run
        Label(window, bg='#9FE849', padx=30, relief=RIDGE, text=count_standby, font="Arial 15 bold").grid(row=12, column=col, sticky=W, padx=50)
        Label(window, bg='#9FE849', padx=30, relief=RIDGE, text=duration_standby, font="Arial 15 bold").grid(row=12, column=col, sticky=E, padx=60)
        Label(window, bg=window_colour, text=str(round(stop_dur, 2)) + ' %', font="Arial 15 bold").grid(row=12, column=col + 1, sticky=W)
        # Stand By
        Label(window, bg='#F5F372', padx=30, relief=RIDGE, text=count_standby, font="Arial 15 bold").grid(row=13, column=col, sticky=W, padx=50)
        Label(window, bg='#F5F372', padx=30, relief=RIDGE, text=duration_standby, font="Arial 15 bold").grid(row=13, column=col, sticky=E, padx=60)
        Label(window, bg=window_colour, text=str(round(stop_dur, 2)) + ' %', font="Arial 15 bold").grid(row=13, column=col + 1, sticky=W)
        # Stop
        Label(window, bg='#F57272', padx=30, relief=RIDGE, text=count_stop, font="Arial 15 bold").grid(row=14, column=col, sticky=W, padx=50, ipadx=5)
        Label(window, bg='#F57272', padx=30, relief=RIDGE, text=duration_stop, font="Arial 15 bold").grid(row=14, column=col, sticky=E, padx=60)
        Label(window, bg=window_colour, text=str(round(stop_dur, 2)) + ' %', font="Arial 15 bold").grid(row=14, column=col + 1, sticky=W)

    # Raw Material
    current_conveyor_capacity_buffer(0, 25, 500, 5000, "Cur Level / Stock")

    # Depall
    D_BL3, D_BL2, D_BL1 = machine_beacon(1, 'DEPALL')
    current_machine_buffer_and_brake(1, 125, 1000, 3000, "Level / Capacity")
    kpis(1, '14', '12h 21min', '3', '6h 30min')

    # Depall - Filler conveyor
    current_conveyor_capacity_buffer(2, 25, 500, 5000, "Depall Level / Capacity")

    # Filler
    F_BL3, F_BL2, F_BL1 = machine_beacon(3, 'FILLER')
    current_machine_buffer_and_brake(3, 135, 100, 200, "Level / Capacity")
    kpis(3, '20', '19h 1min', '5', '21h 30min')

    # Filler - Pasteur conveyor
    current_conveyor_capacity_buffer(4, 25, 500, 5000, "Depall Level / Capacity")

    # Pasteur
    P_BL3, P_BL2, P_BL1 = machine_beacon(5, 'PASTEUR')
    current_machine_buffer_and_brake(5, 115, 10000, 20000, "Level / Capacity")
    kpis(5, '5', '6h 21min', '12', '19h 30min')

    # Pasteur - _  conveyor
    current_conveyor_capacity_buffer(6, 25,  500, 5000, "Depall Level / Capacity")

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
