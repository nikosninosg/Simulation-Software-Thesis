from tkinter import *
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
    root.geometry("1020x900")
    bg_colour = '#DEF9FB'
    root.configure(bg=bg_colour)

    Label(root, anchor=CENTER, text='Καλωσόρισες στο Πρόγραμμα Προσομοίωσης Συσκευασίας Κουτιού Μπύρας.',
          font="Arial 20 bold", bg='light green', pady=15).grid(row=0, sticky=EW)

    # Create a photo image object of the image in the path
    test = ImageTk.PhotoImage(Image.open("images\\img1.jpg"))
    L1 = Label(image=test, bg=bg_colour,)
    L1.image = test
    # Position image
    L1.place(bordermode=OUTSIDE, x=180, y=350)

    # Entries
    # DT
    Label(root, bg=bg_colour, text="Ακρίβεια υπολογισμού αποτελεσμάτων (dt in seconds):", font="Arial 15 bold ").grid(row=1, padx=60, sticky=W)
    dt = IntVar()
    Entry(root, textvariable=dt, bd=5, font="Arial 13 bold").grid(row=1, sticky=E, padx=230)
    # Shift
    shift = IntVar()
    Label(root, bg=bg_colour, text="Αριθμός βαρδιών παραγωγής (shift in seconds):", font="Arial 15 bold ").grid(row=2, padx=60, sticky=W)
    Entry(root, textvariable=shift, bd=5, font="Arial 13 bold").grid(row=2, sticky=E, padx=230, pady=20)

    # Breakdown Title
    Label(root, bg='light blue', anchor=CENTER, text='Breakdown Option', font="Arial 18 bold", pady=5).grid(row=3, sticky=EW)
    # Automated Breakdown
    auto_break_var = IntVar()
    Checkbutton(root, bg=bg_colour, text="Αυτόματη Βλάβη (Πιθανοτική)", font="Arial 15 bold", variable=auto_break_var).grid(row=4, padx=40, pady=20, sticky=W)
    # Manual Breakdown
    manual_break_var = IntVar()
    Checkbutton(root, bg=bg_colour, text="Χειροκίνητη Βλάβη (Break Button):", font="Arial 15 bold", variable=manual_break_var).grid(row=5, padx=40, sticky=W)
    # Checkbutton(root, text="Χειροκίνητη Βλάβη τη στιγμή προσομοίωσης (minutes):", font="Arial 15 bold", variable=manual_break_var).grid(row=5, padx=40, sticky=W)
    # manual_sim_time = IntVar()
    # Entry(root, bd=4, textvariable=manual_sim_time, font="Arial 13 bold").grid(row=5, padx=230, sticky=E)

    # Close Button
    Button(root, text='Start Simulation', height=2, width=15, font="Arial 15 bold ", bd='5', bg='#C1C0C0', activebackground='cyan', command=root.destroy).grid(row=8, sticky='S', pady=500)

    root.mainloop()

    if auto_break_var.get() == manual_break_var.get():
        print("Επέλεξες και τις 2 επιλογές. Ξανά προσπάθησε.")
        welcomeScreen()

    return manual_break_var.get(), shift.get(), dt.get()


# a, b, c = welcomeScreen()
# print(a, b, c)

'''

WEEKS = 5  # Simulation time in weeks
SIM_TIME = WEEKS * 7 * 24 * 60  # Simulation time in minutes

dictTI = brakeOption()
print(dictTI)

if "Depall" in dictTI:
    print("Depall found")
else:
    print('Depall not found')
'''
