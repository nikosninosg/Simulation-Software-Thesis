import random
from tkinter import *
from functools import partial
from PIL import ImageTk, Image

dt = 1000
count = 3
duration = '2h 22min'


def liveMonitoring():
    window = Tk()
    window_colour = '#D6EBFE'
    window.title("Live Process Monitoring!")
    window.configure(bg=window_colour)
    current_ptime = 10
    window.geometry('1900x900')

    Label(bg="light blue",  relief=GROOVE, text="LIVE TIME SIMULATION", font="Arial 25 bold").grid(row=0, column=2, pady=5)

    # Depall
    # Image
    img_depall = ImageTk.PhotoImage(Image.open("images\\depall.png").resize((350, 260)))
    imgD = Label(image=img_depall, bd=4, width=350, height=260, justify=LEFT, padx=100, relief=RAISED, text='Depall', font="Arial 15 bold")
    imgD.grid(row=4, column=1, padx=100, sticky=W)
    # Φάρος
    l1_3 = Label(bg='#FAB3B3', bd=4, width=3, height=2, relief=RAISED)
    l1_3.grid(row=1, column=1, padx=265, sticky=W)
    l1_2 = Label(bg='#FFDAB3', bd=4, width=3, height=2, relief=RAISED)
    l1_2.grid(row=2, column=1, padx=265, sticky=W)
    l1_1 = Label(bg='#D9F2CC', bd=4, width=3, height=2, relief=RAISED)
    l1_1.grid(row=3, column=1, padx=265, sticky=W)
    # Name
    l1_0 = Label(bg='#8DCDBA', bd=4, relief=RAISED, text='DEPALL', font="Arial 15 bold")
    l1_0.grid(row=3, column=1, padx=100, sticky=W)

    # Filler
    # Image
    img_filler = ImageTk.PhotoImage(Image.open("images\\filler.png").resize((350, 260)))
    imgF = Label(image=img_filler, bd=4, width=350, height=260, justify=LEFT, padx=100, relief=RAISED, text='Filler', font="Arial 15 bold")
    imgF.grid(row=4, column=2, padx=100, sticky=W)
    # Φάρος
    l2_3 = Label(bg='red', bd=4, width=3, height=2, relief=RAISED)
    l2_3.grid(row=1, column=2, padx=265, sticky=W)
    l2_2 = Label(bg='orange', bd=4, width=3, height=2, relief=RAISED)
    l2_2.grid(row=2, column=2, padx=265, sticky=W)
    l2_1 = Label(bg='light green', bd=4, width=3, height=2, relief=RAISED)
    l2_1.grid(row=3, column=2, padx=265, sticky=W)
    # Name
    l2_0 = Label(bg='#8DCDBA', bd=4, relief=RAISED, text='FILLER', font="Arial 15 bold")
    l2_0.grid(row=3, column=2, padx=100, sticky=W)

    # Pasteur
    img_pasteur = ImageTk.PhotoImage(Image.open("images\\pasteur.png").resize((350, 260)))
    imgP = Label(image=img_pasteur, bd=4, width=350, height=260, padx=100, relief=RAISED, text='Past', font="Arial 15 bold ")
    imgP.grid(row=4, column=3, padx=100, sticky=W)
    # Φάρος
    l3_3 = Label(bg='#FAB3B3', bd=4, width=3, height=2, relief=RAISED)
    l3_3.grid(row=1, column=3, padx=265, sticky=W)
    l3_2 = Label(bg='#FFDAB3', bd=4, width=3, height=2, relief=RAISED)
    l3_2.grid(row=2, column=3, padx=265, sticky=W)
    l3_1 = Label(bg='#D9F2CC', bd=4, width=3, height=2, relief=RAISED)
    l3_1.grid(row=3, column=3, padx=265, sticky=W)
    # Name
    l3_0 = Label(bg='#8DCDBA', bd=4, relief=RAISED, text='PASTEUR', font="Arial 15 bold")
    l3_0.grid(row=3, column=3, padx=100, sticky=W)

    # Current Process Time
    pt = Label(bg='#BFFCBC', bd=4, height=2, justify=CENTER, relief=RAISED,
               text='Current Process Time: ' + str(current_ptime) + '  seconds', font="Arial 13 bold ")
    pt.grid(row=5, column=2, pady=35)

    Label(bg='light grey', padx=10, relief=GROOVE, text='STAND BY:', font="Arial 15 bold").grid(row=7, column=0)
    Label(bg='light grey', padx=10, relief=GROOVE, text='STOP:', font="Arial 15 bold").grid(row=8, column=0, pady=10)

    # ----RCA----
    def rca_output(col, count_standby, duration_standby, count_stop, duration_stop):
        Label(bg=window_colour, text='COUNT', font="Arial 15 bold").grid(row=6, column=col, sticky=W, padx=150)
        Label(bg=window_colour, text='DURATION', font="Arial 15 bold").grid(row=6, column=col, sticky=E, padx=170)
        # Stand By
        Label(bg='white', padx=30, relief=RIDGE, text=count_standby, font="Arial 15 bold").grid(row=7, column=col, sticky=W, padx=150)
        Label(bg='white', padx=30, relief=RIDGE, text=duration_standby, font="Arial 15 bold").grid(row=7, column=col, sticky=E, padx=145)
        # Stop
        Label(bg='white', padx=30, relief=RIDGE, text=count_stop, font="Arial 15 bold").grid(row=8, column=col, sticky=W, padx=150)
        Label(bg='white', padx=30, relief=RIDGE, text=duration_stop, font="Arial 15 bold").grid(row=8, column=col, sticky=E, padx=145)

    # Depall
    rca_output(1, '24', '22h 21min', '3', '6h 30min')

    # Filler
    rca_output(2, '20', '9h 21min', '15', '21h 30min')

    # Pasteur
    rca_output(3, '15', '6h 21min', '12', '9h 30min')

    ll3 = ['red', '#FAB3B3']
    ll2 = ['orange', '#FFDAB3']
    ll1 = ['green', '#D9F2CC']

    # Update
    def update():
        l1_3['bg'] = random.choice(ll3)
        l1_2['bg'] = random.choice(ll2)
        l1_1['bg'] = random.choice(ll1)

        l2_3['bg'] = random.choice(ll3)
        l2_2['bg'] = random.choice(ll2)
        l2_1['bg'] = random.choice(ll1)

        l3_3['bg'] = random.choice(ll3)
        l3_2['bg'] = random.choice(ll2)
        l3_1['bg'] = random.choice(ll1)

        pt['text'] = 'Current Process Time: ' + str(current_ptime) + '  minutes'
        window.after(dt, update)

    update()

    # Close Button
    Button(window, text="Close", height=2, width=10, font="Arial 12 bold ", bd='5', bg='#479997',
           command=window.destroy).grid(row=9, column=2, pady=70)

    window.resizable(True, True)
    window.mainloop()


# liveMonitoring()


# ---------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------


def machine_details_window(machine_name):
    """Details Of Machine"""

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

    Button(root, text="Close", height=2, width=10, font="Arial 12 bold ", justify=CENTER, bd='5', bg='#479997',
           command=root.destroy).grid(row=9, column=2, pady=70)
    print(root.state())
    root.resizable(True, True)
    root.mainloop()


def live_monitoring():
    """Live Simulation Monitoring"""

    window = Tk()
    window_colour = '#D6EBFE'
    window.title("Live Process Monitoring!")
    window.configure(bg=window_colour)
    pc_time = 10
    window.geometry('1900x900')

    # Title
    Label(window, bg="light blue",  relief=GROOVE, text="LIVE TIME SIMULATION", font="Arial 25 bold").grid(row=0, column=2, pady=5)
    # Stand By
    Label(window, bg='light grey', padx=10, relief=GROOVE, text='STAND BY:', font="Arial 15 bold").grid(row=7, column=0)
    # Stop
    Label(window, bg='light grey', padx=10, relief=GROOVE, text='STOP:', font="Arial 15 bold").grid(row=8, column=0, pady=10)

    # Current Process Time
    pt = Label(window, bg='#BFFCBC', bd=4, height=2, justify=CENTER, relief=RAISED,
               text='Current Process Time: ' + str(pc_time) + '  seconds', font="Arial 13 bold ")
    pt.grid(row=5, column=2, pady=35)

    # Image Depall
    imgD = ImageTk.PhotoImage(Image.open("images\\depall.png").resize((350, 260)))
    Label(window, image=imgD, bd=4, width=350, height=260, padx=100, relief=RAISED).grid(row=4, column=1, padx=100, sticky=W)
    # Image Filler
    imgF = ImageTk.PhotoImage(Image.open("images\\filler.png").resize((350, 260)))
    Label(window, image=imgF, bd=4, width=350, height=260, padx=100, relief=RAISED).grid(row=4, column=2, padx=100, sticky=W)
    # Image Pasteur
    imgP = ImageTk.PhotoImage(Image.open("images\\pasteur.png").resize((350, 260)))
    Label(window, image=imgP, bd=4, width=350, height=260, padx=100, relief=RAISED).grid(row=4, column=3, padx=100, sticky=W)

    def machine_object(col, machine_name):
        # Φάρος
        LB3 = Label(window, bg='#FAB3B3', bd=4, width=3, height=2, relief=RAISED)
        LB3.grid(row=1, column=col, padx=265, sticky=W)
        LB2 = Label(window, bg='#FBF3C1', bd=4, width=3, height=2, relief=RAISED)
        LB2.grid(row=2, column=col, padx=265, sticky=W)
        LB1 = Label(window, bg='#D9F2CC', bd=4, width=3, height=2, relief=RAISED)
        LB1.grid(row=3, column=col, padx=265, sticky=W)
        # Name
        Button(window, bg='#8DCDBA', bd=4, relief=RAISED, text=machine_name, font="Arial 13 bold", command=partial(machine_details_window, machine_name)).grid(row=3, column=col, padx=100, sticky=W)

        return LB3, LB2, LB1

    def kpis(col, count_standby, duration_standby, count_stop, duration_stop):
        Label(window, bg=window_colour, text='COUNT', font="Arial 15 bold").grid(row=6, column=col, sticky=W, padx=150)
        Label(window, bg=window_colour, text='DURATION', font="Arial 15 bold").grid(row=6, column=col, sticky=E, padx=170)
        # Stand By
        Label(window, bg='white', padx=30, relief=RIDGE, text=count_standby, font="Arial 15 bold").grid(row=7, column=col, sticky=W, padx=150)
        Label(window, bg='white', padx=30, relief=RIDGE, text=duration_standby, font="Arial 15 bold").grid(row=7, column=col, sticky=E, padx=145)
        # Stop
        Label(window, bg='white', padx=30, relief=RIDGE, text=count_stop, font="Arial 15 bold").grid(row=8, column=col, sticky=W, padx=150)
        Label(window, bg='white', padx=30, relief=RIDGE, text=duration_stop, font="Arial 15 bold").grid(row=8, column=col, sticky=E, padx=145)

    # Depall
    D_BL3, D_BL2, D_BL1 = machine_object(1, 'DEPALL')
    kpis(1, '4', '2h 21min', '3', '6h 30min')

    # Filler
    F_BL3, F_BL2, F_BL1 = machine_object(2, 'FILLER')
    kpis(2, '20', '9h 21min', '5', '21h 30min')

    # Pasteur
    P_BL3, P_BL2, P_BL1 = machine_object(3, 'PASTEUR')
    kpis(3, '5', '6h 21min', '12', '9h 30min')

    ll3 = ['red', '#FAB3B3']
    ll2 = ['yellow', '#FFDAB3']
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
           command=window.destroy).grid(row=9, column=2, pady=70)

    window.resizable(True, True)
    window.mainloop()


live_monitoring()


'''
def liveMonitoring():
    window = Tk()
    window_colour = '#D6EBFE'
    window.title("Live Process Monitoring!")
    window.configure(bg=window_colour)
    current_ptime = 10
    window.geometry('1900x900')

    Label(bg=window_colour).grid(row=0, pady=5)

    # Depall
    # Image
    img_depall = ImageTk.PhotoImage(Image.open("images\\depall.png").resize((350, 260)))
    imgD = Label(image=img_depall, bd=4, width=350, height=260, justify=LEFT, padx=100, relief=RAISED, text='Depall', font="Arial 15 bold")
    imgD.grid(row=4, column=1, padx=100, sticky=W)
    # Φάρος
    l1_3 = Label(bg='#FAB3B3', bd=4, width=3, height=2, relief=RAISED)
    l1_3.grid(row=1, column=1, padx=265, sticky=W)
    l1_2 = Label(bg='#FFDAB3', bd=4, width=3, height=2, relief=RAISED)
    l1_2.grid(row=2, column=1, padx=265, sticky=W)
    l1_1 = Label(bg='#D9F2CC', bd=4, width=3, height=2, relief=RAISED)
    l1_1.grid(row=3, column=1, padx=265, sticky=W)
    # Name
    l1_0 = Label(bg='#8DCDBA', bd=4, relief=RAISED, text='DEPALL', font="Arial 15 bold")
    l1_0.grid(row=3, column=1, padx=100, sticky=W)

    # Filler
    # Image
    img_filler = ImageTk.PhotoImage(Image.open("images\\filler.png").resize((350, 260)))
    imgF = Label(image=img_filler, bd=4, width=350, height=260, justify=LEFT, padx=100, relief=RAISED, text='Filler', font="Arial 15 bold")
    imgF.grid(row=4, column=2, padx=100, sticky=W)
    # Φάρος
    l2_3 = Label(bg='red', bd=4, width=3, height=2, relief=RAISED)
    l2_3.grid(row=1, column=2, padx=265, sticky=W)
    l2_2 = Label(bg='orange', bd=4, width=3, height=2, relief=RAISED)
    l2_2.grid(row=2, column=2, padx=265, sticky=W)
    l2_1 = Label(bg='light green', bd=4, width=3, height=2, relief=RAISED)
    l2_1.grid(row=3, column=2, padx=265, sticky=W)
    # Name
    l2_0 = Label(bg='#8DCDBA', bd=4, relief=RAISED, text='FILLER', font="Arial 15 bold")
    l2_0.grid(row=3, column=2, padx=100, sticky=W)

    # Pasteur
    img_pasteur = ImageTk.PhotoImage(Image.open("images\\pasteur.png").resize((350, 260)))
    imgP = Label(image=img_pasteur, bd=4, width=350, height=260, padx=100, relief=RAISED, text='Past', font="Arial 15 bold ")
    imgP.grid(row=4, column=3, padx=100, sticky=W)
    # Φάρος
    l3_3 = Label(bg='#FAB3B3', bd=4, width=3, height=2, relief=RAISED)
    l3_3.grid(row=1, column=3, padx=265, sticky=W)
    l3_2 = Label(bg='#FFDAB3', bd=4, width=3, height=2, relief=RAISED)
    l3_2.grid(row=2, column=3, padx=265, sticky=W)
    l3_1 = Label(bg='#D9F2CC', bd=4, width=3, height=2, relief=RAISED)
    l3_1.grid(row=3, column=3, padx=265, sticky=W)
    # Name
    l3_0 = Label(bg='#8DCDBA', bd=4, relief=RAISED, text='PASTEUR', font="Arial 15 bold")
    l3_0.grid(row=3, column=3, padx=100, sticky=W)

    # Current Process Time
    pt = Label(bg='#BFFCBC', bd=4, height=2, justify=CENTER, relief=RAISED,
               text='Current Process Time: ' + str(current_ptime) + '  seconds', font="Arial 13 bold ")
    pt.grid(row=5, column=2, pady=35)

    # ----RCA----
    def rca_output(col, count_standby, duration_standby, count_stop, duration_stop):
        Label(bg=window_colour, text='COUNT', font="Arial 15 bold").grid(row=6, column=col, sticky=W, padx=160)
        Label(bg=window_colour, text='DURATION', font="Arial 15 bold").grid(row=6, column=col, sticky=E, padx=180)
        # Stand By
        Label(bg='white', padx=30, relief=RIDGE, text=count_standby, font="Arial 15 bold").grid(row=7, column=col, sticky=W, padx=160)
        Label(bg='white', padx=30, relief=RIDGE, text=duration_standby, font="Arial 15 bold").grid(row=7, column=col, sticky=E, padx=160)
        # Stop
        Label(bg='white', padx=30, relief=RIDGE, text=count_stop, font="Arial 15 bold").grid(row=8, column=col, sticky=W, padx=160)
        Label(bg='white', padx=30, relief=RIDGE, text=duration_stop, font="Arial 15 bold").grid(row=8, column=col, sticky=E, padx=160)

    # Depall
    Label(bg=window_colour, text='COUNT', font="Arial 15 bold").grid(row=6, column=1, sticky=W, padx=160)
    Label(bg=window_colour, text='DURATION', font="Arial 15 bold").grid(row=6, column=1, sticky=E, padx=180)
    Label(bg='light grey', padx=10, relief=GROOVE, text='STAND BY:', font="Arial 15 bold").grid(row=7, column=0)
    Label(bg='white', padx=30, relief=RIDGE, text=count, font="Arial 15 bold").grid(row=7, column=1, sticky=W, padx=160)
    Label(bg='white', padx=30, relief=RIDGE, text=duration, font="Arial 15 bold").grid(row=7, column=1, sticky=E, padx=160)
    Label(bg='white', padx=30, relief=RIDGE, text=count, font="Arial 15 bold").grid(row=8, column=1, sticky=W, padx=160)
    Label(bg='white', padx=30, relief=RIDGE, text=duration, font="Arial 15 bold").grid(row=8, column=1, sticky=E, padx=160)

    # Filler
    Label(bg=window_colour, text='COUNT', font="Arial 15 bold").grid(row=6, column=2, sticky=W, padx=160)
    Label(bg=window_colour, text='DURATION', font="Arial 15 bold").grid(row=6, column=2, sticky=E, padx=180)
    Label(bg='light grey', padx=10, relief=GROOVE, justify=LEFT, text='STOP:', font="Arial 15 bold").grid(row=8, column=0, pady=10)
    Label(bg='white', padx=30, relief=RIDGE, text=count, font="Arial 15 bold").grid(row=7, column=2, sticky=W, padx=160)
    Label(bg='white', padx=30, relief=RIDGE, text=duration, font="Arial 15 bold").grid(row=7, column=2, sticky=E, padx=160)
    Label(bg='white', padx=30, relief=RIDGE, text=count, font="Arial 15 bold").grid(row=8, column=2, sticky=W, padx=160)
    Label(bg='white', padx=30, relief=RIDGE, text=duration, font="Arial 15 bold").grid(row=8, column=2, sticky=E, padx=160)

    # Pasteur
    Label(bg=window_colour, text='COUNT', font="Arial 15 bold").grid(row=6, column=3, sticky=W, padx=160)
    Label(bg=window_colour, text='DURATION', font="Arial 15 bold").grid(row=6, column=3, sticky=E, padx=180)
    Label(bg='light grey', padx=10, relief=GROOVE, text='STOP:', font="Arial 15 bold").grid(row=8, column=0, pady=10)
    Label(bg='white', padx=30, relief=RIDGE, text=count, font="Arial 15 bold").grid(row=7, column=3, sticky=W, padx=160)
    Label(bg='white', padx=30, relief=RIDGE, text=duration, font="Arial 15 bold").grid(row=7, column=3, sticky=E, padx=160)
    Label(bg='white', padx=30, relief=RIDGE, text=count, font="Arial 15 bold").grid(row=8, column=3, sticky=W, padx=160)
    Label(bg='white', padx=30, relief=RIDGE, text=duration, font="Arial 15 bold").grid(row=8, column=3, sticky=E, padx=160)

    ll3 = ['red', '#FAB3B3']
    ll2 = ['orange', '#FFDAB3']
    ll1 = ['green', '#D9F2CC']

    # Update
    def update():
        l1_3['bg'] = random.choice(ll3)
        l1_2['bg'] = random.choice(ll2)
        l1_1['bg'] = random.choice(ll1)

        l2_3['bg'] = random.choice(ll3)
        l2_2['bg'] = random.choice(ll2)
        l2_1['bg'] = random.choice(ll1)

        l3_3['bg'] = random.choice(ll3)
        l3_2['bg'] = random.choice(ll2)
        l3_1['bg'] = random.choice(ll1)

        pt['text'] = 'Current Process Time: ' + str(current_ptime) + '  minutes'
        window.after(dt, update)

    update()

    # Close Button
    Button(window, text="Close", height=2, width=10, font="Arial 12 bold ", bd='5', bg='#479997',
           command=window.destroy).grid(row=9, column=2, pady=70)

    window.resizable(True, True)
    window.mainloop()


liveMonitoring()


'''