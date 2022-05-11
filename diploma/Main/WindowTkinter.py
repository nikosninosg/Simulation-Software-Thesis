from tkinter import *
from Converters import *
from tkinter import messagebox
from PIL import ImageTk, Image


def displayNotification(txt):
    """Προσθήκη πρώτης ύλης"""

    def get_variable_value():
        # value_result.set(val.get())  # assign val variable to other
        # print(value_result.get())  # if you want see the result in the console
        window.destroy()
        return value_result.get()

    # declare the window
    window = Tk()

    # val = IntVar()

    value_result = IntVar()

    # set window title
    window.title("ΑΤΤΕΝΤΙΟΝ!")

    # set window width and height
    # window.configure(width=500, height=300)
    window.geometry("900x500")
    # window.resizable(False, False)
    # set window background color
    window.configure(bg='#E89D77')

    # image mesa sto label
    L = Label(window, anchor=CENTER, text=txt, bg='#E89D77', font="Arial 19 bold", pady=100)
    L.pack()
    Label(window, pady=10, bg='#E89D77').pack()
    Label(window, text='Πόσα παλεταρισμένα κουτιά προσέθεσες ως πρώτη ύλη στο Depall?', font=("Arial", 15)).pack()
    # value  = Entry(window, justify='left', textvariable = val).pack()

    # B = Button(window, text="OK", bd='5', command=window.destroy).pack(side='bottom')
    Button(window, text="OK", bd='7', command=get_variable_value, height=2, width=7, font="Arial 15 bold ").pack(
        side='bottom')
    Entry(window, justify='left', bd=4, textvariable=value_result).pack()

    # print(res)
    # Bind the Enter Key to Call an event
    # window.bind('<Return>')
    window.mainloop()

    return value_result.get()


# Display = displayNotification('Έχει μειωθεί σημαντικά το απόθεμα πρώτης ύλης στο Depall. \n Χρειάζεται ανατροφοδότηση.')


# print("Ο χειριστής πρόσθεσε %d παλεταρισμένα κουτιά." % v)
# print(type(Display))


def displayAlert(ftext, stime):
    """Γενική συνάρτηση Προειδοποίησης (Παράθυρο με μήνυμα)"""
    window = Tk()

    # set window title
    window.title("System Alert")

    # set window width and height
    # window.configure(width=500, height=300)
    window.geometry("850x500")
    # window.resizable(False, False)
    # set window background color
    window.configure(bg='orange')

    # ftext = "Το μηχάνημα " + machine + " έχει τεθεί σε κατάσταση:" + status + "\n Αιτία: " + cause

    # image mesa sto label
    L = Label(window, anchor=CENTER, text=ftext, font="Arial 20 bold", bg='orange')
    L.grid(row=0, column=0, pady=10)
    Label(window, anchor=CENTER, text='Simulation Time = ' + str(round(stime, 2)), bd=10, font="Arial 20 bold").grid(
        column=0, row=1, pady=50)

    Button(window, text="OK! Am checking it.", height=5, width=20, font="Arial 15 bold ", bd='5',
           command=window.destroy).grid(row=2, column=0, pady=50)

    window.mainloop()


# displayAlert("O Filler έχει τεθεί σε κατάσταση Stand By (Status = ORANGE).\n Αιτία: Δεν έχει 1 κουτί να εισάγει. ", 10.02)

def displayStop(ftext, stime):
    """Γενική συνάρτηση ενημέρωσης σταματήματος (Παράθυρο με μήνυμα)"""

    window = Tk()
    bg_colour = 'red'
    # set window title
    window.title("System Alert")

    # set window width and height
    # window.configure(width=500, height=300)
    window.geometry("850x500")
    # window.resizable(False, False)
    # set window background color
    window.configure(bg=bg_colour)

    # ftext = "Το μηχάνημα " + machine + " έχει τεθεί σε κατάσταση:" + status + "\n Αιτία: " + cause

    # image mesa sto label
    L = Label(window, anchor=CENTER, text=ftext, font="Arial 20 bold", bg=bg_colour)
    L.grid(row=0, column=0, pady=10)
    Label(window, anchor=CENTER, text='Simulation Time = ' + str(round(stime, 2)), bd=10, font="Arial 20 bold", bg=bg_colour).grid(
        column=0, row=1, pady=50)

    Button(window, text="OK! Am checking it.", height=5, width=20, font="Arial 15 bold ", bd='5',
           command=window.destroy).grid(row=2, column=0, pady=50)

    window.mainloop()


# displayStop("O Filler έχει τεθεί εκτός λειτουργίας (Status = RED).\n Αιτία: Φρακαρισμένη έξοδος.", 10.02)


# -----------------------------------


def wrongValue():
    """Έλεγχος της εισαγόμενης τιμής"""
    master = Tk()

    master.geometry("385x260")

    master.title("Λάθος τιμή")
    Label(master,
          text="Έδωσες λάθος τιμή. Ξανά προσπάθησε",
          anchor=CENTER, font="Arial 15 bold", bg='light blue', pady=50).grid()

    Button(master, text='OK', height=2, width=10, font="Arial 15 bold ", bd='5', bg='#C1C0C0', activebackground='red',
           command=master.destroy).grid(row=8, sticky='S', pady=30)
    master.mainloop()


# wrongValue()
dictT = {}


# global dictT


def triggerStopList(sim_time):
    master = Tk()

    master.title("Επιλογή μηχανήματος σε status Red.")

    Label(master,
          text="Ποιο/α μηχανήματα θέλεις να θέσεις σε κατάσταση εκτός λειτουργίας? \nStatus: Red = Stopped :",
          anchor=CENTER, font="Arial 20 bold", bg='light blue', pady=50).grid(row=0)

    # Depall
    var1 = IntVar()
    Checkbutton(master, text="Depall", font="Arial 20 bold", variable=var1).grid(row=1, column=0, sticky=W)
    Label(master, text="Επέλεξε τη στιγμή που θα σταματήσει το Depall (100 - %d min)" % (sim_time - 4000),
          font="Arial 15 bold").grid(
        row=1, column=0)
    depallTimeRes = IntVar()
    Entry(master, justify='right', bd=4, textvariable=depallTimeRes).grid(row=1, column=0, sticky=E)

    # Filler
    var2 = IntVar()
    Checkbutton(master, text="Filler", font="Arial 20 bold", variable=var2).grid(row=2, sticky=W)
    Label(master, text="Επέλεξε τη στιγμή που θα σταματήσει ο Filler (200 - %d min)" % (sim_time - 3000),
          font="Arial 15 bold").grid(
        row=2, column=0)
    fillerTimeRes = IntVar()
    Entry(master, justify='right', bd=4, textvariable=fillerTimeRes).grid(row=2, column=0, sticky=E)

    # Pasteur
    var3 = IntVar()
    Checkbutton(master, text="Pasteur", font="Arial 20 bold", variable=var3).grid(row=3, sticky=W)
    Label(master, text="Επέλεξε τη στιγμή που θα σταματήσει ο Pasteur (300 - %d min)" % (sim_time - 2000),
          font="Arial 15 bold").grid(
        row=3, column=0)
    pasteurTimeRes = IntVar()
    Entry(master, justify='right', bd=4, textvariable=pasteurTimeRes).grid(row=3, column=0, sticky=E)

    # Label(master).grid(row=5, column=0)
    # Label(master).grid(row=6, column=0)
    # Label(master).grid(row=7, column=0)
    Button(master, text='OK', height=2, width=10, font="Arial 15 bold ", bd='5', bg='#C1C0C0', activebackground='red',
           command=master.destroy).grid(row=8, sticky='S', pady=100)

    master.geometry("930x500")

    master.mainloop()

    if var1.get() == 1:
        if 100 <= depallTimeRes.get() <= (sim_time - 4000):
            dictT['Depall'] = depallTimeRes.get()
        else:
            wrongValue()
            print("Έδωσες λάθος τιμή στο Filler")
            triggerStopList(sim_time)

    if var2.get() == 1:
        if 200 <= fillerTimeRes.get() <= (sim_time - 3000):
            dictT['Filler'] = fillerTimeRes.get()
        else:
            wrongValue()
            print("Έδωσες λάθος τιμή στο Filler")
            triggerStopList(sim_time)

    if var3.get() == 1:
        if 300 <= pasteurTimeRes.get() <= (sim_time - 2000):
            dictT['Pasteur'] = pasteurTimeRes.get()
        else:
            wrongValue()
            print("Έδωσες λάθος τιμή στο Pasteur")
            triggerStopList(sim_time)

    return dictT


# dct = triggerStopList(45500)
# for key, value in dct.items():
#    print(key, ' : ', value)


def breakdownOption(sim_time_):
    """Welcome Screen"""
    root = Tk()
    root.geometry("1020x700")
    Label(root, anchor=CENTER, text='Καλωσόρισες στο Πρόγραμμα Προσομοίωσης Συσκευασίας Κουτιού Μπύρας.',
          font="Arial 20 bold", bg='light green', pady=100).pack()

    # Create a photo image object of the image in the path
    image1 = Image.open("images\\img1.jpg")
    test = ImageTk.PhotoImage(image1)

    label1 = Label(image=test)
    label1.image = test

    # Position image
    label1.place(x=180, y=250)

    res = messagebox.askyesno(title="Επιλογή Περίπτωσης Αποτυχίας",
                              message='Θές να προκαλέσεις βλάβη σε κάποιο μηχάνημα? (Status = RED)')

    if res:
        root.destroy()
        # print("Πάτησες Ναι")
        dictionaryT = triggerStopList(sim_time_)
        return dictionaryT
    else:
        # print('Πάτησες όχι')
        root.destroy()
        return None


def welcomeScreen():
    """Welcome Screen"""
    root = Tk()
    root.geometry("1000x650")
    bg_colour = '#DEF9FB'
    root.configure(bg=bg_colour)

    Label(root, anchor=CENTER, text='Προσομοίωση Γραμμής Παραγωγής',
          font="Arial 20 bold", bg='light green', pady=15).grid(row=0, columnspan=10, sticky=EW)

    # Create a photo image object of the image in the path
    # test = ImageTk.PhotoImage(Image.open("images\\img1.jpg"))
    # L1 = Label(image=test, bg=bg_colour,)
    # L1.image = test
    # Position image
    # L1.place(bordermode=OUTSIDE, x=180, y=350)

    Label(root, bg=bg_colour).grid(row=1, padx=15, sticky=W)

    # Breakdown Title
    Label(root, bg='light blue', anchor=CENTER, text='Επιλογές Προσομοίωσης', font="Arial 18 bold", pady=5).grid(row=2, columnspan=10, sticky=EW)

    # Entries
    # DT
    dt = IntVar()
    Label(root, bg=bg_colour, text="Βήμα προσομοίωσης (dt):", font="Arial 13 bold ").grid(row=3, column=0, columnspan=2, padx=20, pady=15, sticky=W)
    Entry(root, textvariable=dt, bd=5, font="Arial 13 bold", justify='center').grid(row=3, column=2, sticky=E, padx=0)
    Label(root, bg=bg_colour, text="sec", font="Arial 13 bold ").grid(row=3, column=3, padx=0, sticky=W)

    # T Shift
    shift = IntVar()
    Label(root, bg=bg_colour, text="Συνολικό διάστημα προσομοίωσης (T):", font="Arial 13 bold ").grid(row=4, column=0, columnspan=2, padx=20, pady=0, sticky=W)
    Entry(root, textvariable=shift, bd=5, font="Arial 13 bold", justify='center').grid(row=4, column=2, sticky=E, padx=0, pady=0)
    Label(root, bg=bg_colour, text="hours", font="Arial 13 bold ").grid(row=4, column=3, padx=0, sticky=W)

    # Breakdown Title = Εμφάνιση Βλαβών
    Label(root, bg='light blue', anchor=CENTER, text='Εμφάνιση Βλαβών', font="Arial 18 bold", pady=5).grid(row=5, columnspan=10, pady=25, sticky=EW)
    # Description
    Label(root, bg=bg_colour, anchor=CENTER, text='Κατά τη διάρκεια της προσομοίωσης ο χρήστης δημιουργεί βλάβες στα μηχανήματα και τις επιδιορθώνει όποτε επιθυμεί. ', font="Arial 12").grid(row=6, columnspan=10, padx=20, sticky=W)
    # Automated Explanation
    Label(root, bg=bg_colour, anchor=CENTER, text='Για αυτόματη δημιουργία βλαβών απο τον simulator επιλέξτε το παρακάτω checkbox και συμπληρώστε τις πιθανότητες εμφάνισης ανα μηχάνημα.', font="Arial 12").grid(row=7, padx=20, columnspan=10, pady=5, sticky=W)
    # Automated Breakdown
    auto_break_var = IntVar()
    Checkbutton(root, bg=bg_colour, text="Αυτόματη Εμφάνιση Βλαβών", font="Arial 14 bold", variable=auto_break_var).grid(row=8, columnspan=10, padx=20, pady=10, sticky=W)
    # Description
    Label(root, bg=bg_colour, anchor=CENTER, text='Πιθανότητα βλάβης:', font="Arial 12", pady=5).grid(row=9, padx=20, columnspan=10, pady=10, sticky=W)

    # Set probability for machines
    def probability_set(machine_name, row):
        var = IntVar()
        Label(root, bg=bg_colour, anchor=CENTER, text=machine_name, font="Arial 13 bold", pady=5).grid(row=row, column=0, sticky=W, padx=20, pady=0)
        Entry(root, justify='center', bd=4, font="Arial 13 bold", textvariable=var).grid(row=row, column=1, sticky=W, padx=0)
        Label(root, bg=bg_colour, anchor=CENTER, text="%", font="Arial 13 bold", pady=5).grid(row=row, column=2, sticky=W, padx=0, pady=0)

        return var

    # Depall
    va1 = probability_set('Depall', 10)
    va2 = probability_set('Filler', 11)
    va3 = probability_set('Pasteur', 12)

    # Manual Breakdown
    Label(root, bg=bg_colour).grid(pady=14)
    # manual_break_var = IntVar()
    # Checkbutton(root, bg=bg_colour, text="Χειροκίνητη Βλάβη (Break Button):", font="Arial 15 bold", variable=manual_break_var).grid(row=9, padx=40, sticky=W)
    # Checkbutton(root, text="Χειροκίνητη Βλάβη τη στιγμή προσομοίωσης (minutes):", font="Arial 15 bold", variable=manual_break_var).grid(row=5, padx=40, sticky=W)
    # manual_sim_time = IntVar()
    # Entry(root, bd=4, textvariable=manual_sim_time, font="Arial 13 bold").grid(row=5, padx=230, sticky=E)

    # Close Button
    Button(root, text='Start Simulation', height=2, width=15, font="Arial 15 bold ", bd='5', bg='light green', activebackground='cyan', command=root.destroy).grid(row=3, rowspan=2, column=4, padx=100, pady=30, sticky=E)

    root.mainloop()
    '''
    if auto_break_var.get() == manual_break_var.get():
        print("Επέλεξες και τις 2 επιλογές. Ξανά προσπάθησε.")
        welcomeScreen()'''

    return va1.get(), va2.get(), va3.get(), auto_break_var.get(), shift.get(), dt.get()


# v1, v2, v3, a, b, c = welcomeScreen()
# print(v1, v2, v3, a, b, c)


def outroScreen(SIM_TIME_, PRODUCTION_SPEED_, PASTEUR_OUTPUT_, EXPECTED_CANS_, D_PERC_SB_, D_PERC_STOP_, F_PERC_SB_, F_PERC_STOP_, P_PERC_SB_, P_PERC_STOP_):
    root = Tk()
    root.geometry("900x700")

    bg_colour = '#D6EBFE'
    root.configure(bg=bg_colour)
    # Title
    Label(root, anchor=CENTER, text='Δείκτες απόδοσης γραμμής', font="Arial 16 bold", bg='#4d94ff', pady=7).grid(row=0, sticky=EW, columnspan=5)

    # Total Time Simulation
    Label(root, text="Συνολική Διάρκεια Simulation: " + str(duration_converter(SIM_TIME_)), font="Arial 14", bg=bg_colour, pady=10).grid(row=1, sticky=W, columnspan=5)
    # Production Speed
    Label(root, text="Ταχύτητα παραγωγής της γραμμής: " + str(PRODUCTION_SPEED_) + " cans per second", font="Arial 14", bg=bg_colour, pady=10).grid(row=3, sticky=W, columnspan=5)
    # Produced products
    Label(root, text="Προϊόντα που παράχθηκαν: " + str(PASTEUR_OUTPUT_), font="Arial 14", bg=bg_colour, pady=10).grid(row=4, sticky=W, columnspan=5)
    # Expected Products
    Label(root, text="Προϊόντα που αναμέναμε να παραχθούν: " + str(EXPECTED_CANS_), font="Arial 14", bg=bg_colour, pady=10).grid(row=5, sticky=W, columnspan=5)
    # Overall Production Efficiency
    Label(root, text="Συνολική απόδοση παραγωγής: " + str(round((PASTEUR_OUTPUT_/EXPECTED_CANS_)*100, 2))+'%', font="Arial 14", bg=bg_colour, pady=10).grid(row=6, sticky=W, columnspan=5)

    # Τίτλος για τα ποσοστά
    Label(root, text="Καταστάσεις Μηχανημάτων", font="Arial 16 bold", bg='#4d94ff', pady=7).grid(row=10, sticky=EW, pady=20, columnspan=8)
    Label(root, text='MACHINE', font="Arial 14 bold underline", bg=bg_colour, fg='black').grid(column=0, row=11, padx=30)
    Label(root, text='RUN', font="Arial 14 bold underline", bg=bg_colour, fg='#77D82A').grid(column=1, row=11, padx=30)
    Label(root, text='STAND_BY', font="Arial 14 bold underline", bg=bg_colour, fg='#ffff1a').grid(column=2, row=11, padx=30)
    Label(root, text='STOP', font="Arial 14 bold underline", bg=bg_colour, fg='#BE0000').grid(column=3, row=11, padx=30)

    def percentage(row, machine_name, perc_run, perc_standby, perc_stop):
        Label(root, text=machine_name, font="Arial 14", bg=bg_colour).grid(column=0, row=row, padx=30, pady=15)
        Label(root, text=str(perc_run)+'%', font="Arial 14", bg=bg_colour).grid(column=1, row=row, padx=30, pady=15)
        Label(root, text=str(perc_standby)+'%', font="Arial 14", bg=bg_colour).grid(column=2, row=row, padx=30, pady=15)
        Label(root, text=str(perc_stop)+'%', font="Arial 14", bg=bg_colour).grid(column=3, row=row, padx=30, pady=15)
        # Analysis Button
        Button(root, text=machine_name + ' Analysis', height=0, width=15, font="Arial 12 bold", bd='5', bg='light green',
               activebackground='cyan', command=root.destroy).grid(row=row, column=4, padx=0, pady=15, sticky=W)

    # Depall
    # D_PERC_SB_ = machine_duration_conv_to_perc(D_PERC_SB_, SIM_TIME_)
    # D_PERC_STOP_ = machine_duration_conv_to_perc(D_PERC_STOP_, SIM_TIME_)
    percentage(13, 'DEPALL', round(100 - (D_PERC_SB_ + D_PERC_STOP_), 2), D_PERC_SB_, D_PERC_STOP_)
    # Filler
    # F_PERC_SB_ = machine_duration_conv_to_perc(F_PERC_SB_, SIM_TIME_)
    # F_PERC_STOP_ = machine_duration_conv_to_perc(F_PERC_STOP_, SIM_TIME_)
    percentage(14, 'FILLER', round(100 - (F_PERC_SB_ + F_PERC_STOP_), 2), F_PERC_SB_, F_PERC_STOP_)
    # Pasteur
    # P_PERC_SB_ = machine_duration_conv_to_perc(P_PERC_SB_, SIM_TIME_)
    # P_PERC_STOP_ = machine_duration_conv_to_perc(P_PERC_STOP_, SIM_TIME_)
    percentage(15, 'PASTEUR', round(100 - (P_PERC_SB_ + P_PERC_STOP_), 2), P_PERC_SB_, P_PERC_STOP_)

    root.mainloop()


# outroScreen()

'''
    # Breakdowns
    Label(root, anchor=CENTER, text="Breakdowns", font="Arial 16 bold", bg='#9DF4EB', pady=7).grid(row=9, sticky=EW, pady=40, columnspan=4)
    Label(root, text='MACHINE', font="Arial 14 bold underline", bg=bg_colour).grid(column=0, row=14, padx=30)
    Label(root, text='TIMES', font="Arial 14 bold underline", bg=bg_colour).grid(column=1, row=14, padx=30)
    Label(root, text='DURATION', font="Arial 14 bold underline", bg=bg_colour).grid(column=2, row=14, padx=30)

def breakdown(row, machine_name, dictionary):
    for key, value in dictionary.items():
        Label(root, text=machine_name, font="Arial 14 bold", bg=bg_colour).grid(column=0, row=row + key, padx=30,
                                                                                pady=5)
        Label(root, text=key, font="Arial 14 bold", bg=bg_colour).grid(column=1, row=row + key, padx=30, pady=5)
        Label(root, text=duration_converter(value), font="Arial 14 bold", bg=bg_colour).grid(column=2, row=row + key,
                                                                                             padx=30, pady=5)


word_freq = {1: 5116, 2: 23454, 3: 4223, 4: 73238, 5: 143241}

# OEE + ' ('+str((produced_cans/(CANS_PER_HOUR * SHIFT * 8))*100)+'%)'

breakdown(11, 'DEPALL', word_freq)

breakdown(11 + 1 + int(len(word_freq)), 'FILLER', word_freq)
'''
