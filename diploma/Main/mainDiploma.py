import simpy
import random
import threading
import numpy as np
from enum import Enum
from OutputCSV import *
from Converters import *
from colorama import Fore
from WindowTkinter import *
from functools import partial
import matplotlib.pyplot as plt

# matplotlib.use('Agg')

cans_produced = 0  # Συνολικά παραγμένα κουτιά
depall_total_ptime = []
filler_total_ptime = []
pasteur_total_ptime = []


print('----------------------------------')
print("STARTING SIMULATION")

# Αδειάζει το csv για να γράψει τις νέες τιμές
check_csv()

# -------------------------------------------------

# Parameters
# MANUAL_BRAKE_VAR, SHIFT, DT = welcomeScreen()
MANUAL_BRAKE_VAR = 1
# Ακρίβεια αποτελεσμάτων - παρακολούθησης | Ακρίβεια δευτερολέπτου
DT = 2000  # in seconds

# SIMULATION RUN TIME
SHIFT = 1  # Simulation time in shifts
SIM_TIME = SHIFT * 8 * 60 * 60  # Simulation time in seconds

times = SIM_TIME / DT  # Num of rows in csv

print("Simulation Time = %d seconds" % SIM_TIME)
# ---PRODUCTION---
cans_to_produce = 60000  # cans want to produce per hour
production_speed = round(cans_to_produce / 3600, 2)  # cans per second
print("Production Speed: {0} cans/second and: {1} cans/shift".format(production_speed, cans_to_produce * 8))


print('----------------------------------')

# ---EMPTY CANS---
initial_emptyCans = 30000

# ---DEPALL---
# standard vars
depall_capacity = 50000  # 5000 = 1 παλέτα. Empty cans που μπορούν να περιμένουν μέχρι να επεξεργαστούν
initial_depallCans = 0  # Number αρχικών empty can που έχει το depall
depall_batch = 5000
current_depall_level = 0
depall_critical_buffer = depall_batch  # Παίρνει ανα 500 τα κουτιά για επεξεργασία = DEPALL BATCH
# dynamic vars
DEPALL_SPEED = production_speed  # cans / second
depall_input = depall_batch  # Πόσο προϊόν εισάγει για να επεξεργαστεί (input cans/sec)
depall_output = 1  # Πόσο προϊόν εξάγει μετά την επεξεργασία (output cans/sec)
depall_ptime = depall_output / DEPALL_SPEED  # Depall Process Time
MTBF_depall = 31.03  # standard error se min (MTTF)
# status
depall_status = 'orange'
depall_description = "Έναρξη παραγωγής"

# ---FILLER---
# standard vars
filler_capacity = 4000  # Depalletized cans που μπορούν να περιμένουν μέχρι να επεξεργαστούν
initial_filledCans = 0  # Number αρχικών depall can που έχει ο filler
filler_batch = 1
current_filler_level = 0
filler_critical_buffer = filler_batch
# dynamic vars
FILLER_SPEED = production_speed  # cans / second
filler_input = filler_batch  # Πόσο προϊόν εισάγει για να επεξεργαστεί (input cans/sec)
filler_output = filler_input  # Πόσο προϊόν εξάγει μετά την επεξεργασία (output cans/sec)
filler_ptime = filler_output / FILLER_SPEED  # Filler Process Time
MTBF_filler = 5.34  # standard error se min (MTTF)
# status
filler_status = 'orange'
filler_description = "Έναρξη παραγωγής"

# ---PASTEUR---
# standard vars
pasteur_capacity = 2000  # Filled cans που μπορούν να περιμένουν μέχρι να επεξεργαστούν
initial_pastCans = 0  # Number αρχικών Filled can που έχει ο Pasteur
pasteur_batch = 600
current_pasteur_level = 0
pasteur_critical_buffer = pasteur_batch
# dynamic vars
# PASTEUR_SPEED =  # cans / second
pasteur_min_input = 1  # Πόσο προϊόν εισάγει για να επεξεργαστεί (input cans/sec)
pasteur_batch_serve_time = 30  # seconds
# pasteur_output = pasteur_input  # Πόσο προϊόν εξάγει μετά την επεξεργασία (output cans/sec)
pasteur_ptime = 1800  # Pasteur Process Time 30 minutes
MTBF_pasteur = 25.22  # standard error se min (MTTF)
# status
pasteur_status = 'yellow'
pasteur_description = "Έναρξη παραγωγής"

# ---Machine Breakdown---
# Breakdown Probability
min_prob = 1
max_prob = 1000
# Repair Time = Gauss Distribution
MU = 15
SIGMA = 5

# ---GENERAL VARIABLES---

RANDOM_SEED = 42  # Reproduce the results

# Num of Repairers
numOfRepairers = 3  # Πόσοι τεχνικοί - χειριστές υπάρχουν στη βάρδια

# Break Point
MIN_MTBF = 2  # Min time in Red Status
REPAIR_DURATION = 10.0  # Duration to repair a machine in  1 - 10 minutes

NUM_MACHINES = 3  # Number of machines in Can Production Line

# -------------------------------------------------
# Pandas Dataframe
data = [[0, depall_status, filler_status, pasteur_status]]
# Create the pandas DataFrame
df = pd.DataFrame(data, columns=['ENV_NOW', 'Depall', 'Filler', 'Pasteur'])


# -------------------------------------------------


class Status(Enum):
    green = "RUN"
    yellow = "STAND BY"
    red = "STOP"


def break_and_repair_machine(machine_name, repairers):
    """Εντοπισμός σταματήματος σε μηχάνημα και έναρξη εργασίας επισκευής μηχανήματος"""
    global depall_status, filler_status, pasteur_status
    # if np.random.uniform(low=min_prob, high=max_prob) == 2:  # probability 1/30000

    # Set Status
    if machine_name == 'DEPALL':
        print("Depall break pressed")
        can_pack_line.depall_gen.interrupt()

    elif machine_name == 'FILLER':
        print("Filler break pressed")
        can_pack_line.filler_gen.interrupt()

    elif machine_name == 'PASTEUR':
        print("Pasteur break pressed")
        can_pack_line.pasteur_gen.interrupt()

    else:
        print("Κανένα  απο τα 3 if")

    print('%d: ' % env.now + "Breakdown Detected in Machine: " + machine_name)
    env.timeout(1)  # 1 time unit to detect broke
    print('%d: ' % env.now + "Repair of Machine: " + machine_name + " Started")

    # with repairers.request() as request:
    #    # yield request
    #    rep_time = random.gauss(mu=MU, sigma=SIGMA)
    #    env.timeout(rep_time)

    print('%d: ' % env.now + "Repair of Machine: " + machine_name + " Completed After: %f minutes" % 10.2)


def cans_rejection():
    """1 to 1000 probability to reject a product. Cause: fail product"""
    if np.random.uniform(1, 1000) == 5:
        rejected_cans = np.random.uniform(1, 5)  # reject from 1 to 5 cans
        return rejected_cans
        # yield can_pack_line. .get(rejected_cans)


class CanPackLine(object):

    def __init__(self):
        self.env = env
        # Ορισμός προϊόντων που βγάζει και παίρνει κάθε μηχάνημα
        # RAW MATERIAL
        self.emptyCans = simpy.Container(env, capacity=depall_capacity, init=initial_emptyCans)

        # DEPALL
        self.depallCans = simpy.Container(env, capacity=filler_capacity, init=initial_depallCans)
        self.depallCanControl = env.process(self.depall_can_stock_control())

        # FILLER
        self.filledCans = simpy.Container(env, capacity=pasteur_capacity, init=initial_filledCans)
        self.fillerCanControl = env.process(self.filler_batch_buffer())

        # PASTEUR
        self.pastCans = simpy.Container(env, init=initial_pastCans)
        self.pasteurCanControl = env.process(self.pasteur_batch_buffer())

        self.broken = False
        self.repairers = simpy.Resource(env, capacity=numOfRepairers)

        # PROCESS DECLARE & STARTUP
        self.depall_gen = env.process(depall())
        self.filler_gen = env.process(filler())
        self.pasteur_gen = env.process(pasteur())
        self.status_monitoring_gen = env.process(status_monitoring())
        # self.BR_machine_gen = env.process(self.break_and_repair_machine(self.machine_name, self.repairers))

        # Event
        self.ctrl_reactivate = env.event()

    def depall_can_stock_control(self):
        """Depall Batch: Δεν πρέπει να πέσει κάτω απο depall_batch κουτιά για να μη σταματήσει να λειτουργεί"""
        global depall_status, depall_description
        yield env.timeout(0)

        while True:
            if self.emptyCans.level <= depall_critical_buffer:  # level < 5000

                # Set Depall Buffer Status
                depall_status = Status.yellow.name
                depall_description = Status.yellow.value + ": Το επίπεδο άδειων κουτιών είναι κάτω απο το όριο. (empty < 5000)"

                print('%.2f: ' % env.now + '\x1b[0;30;44m' + 'Έναρξη Εισαγωγής Παλέτας.' + '\x1b[0m')
                print('%.2f: ' % env.now + 'Empty Cans level = {0}'.format(self.emptyCans.level))
                print('%.2f: ' % env.now + "Προστέθηκαν %d παλεταρισμένα κουτιά." % depall_input)

                yield env.timeout(0)  # Εργασία χειριστή
                # displayAlert(
                # "Το Depall έχει τεθεί σε κατάσταση Stand By (Status = ORANGE).\n Αιτία: Έχει πέσει κάτω απο 5.000 κουτιά.", env.now)

                # Pall cans που πρόσθεσε ο χειριστής ως πρώτη ύλη στο depall
                yield can_pack_line.emptyCans.put(depall_input)
                print('%.2f: ' % env.now + 'New empty cans stock is {0}'.format(self.emptyCans.level))
                print('%.2f: ' % env.now + '\x1b[0;30;44m' + 'Τέλος Εισαγωγής παλέτας' + '\x1b[0m')
            elif depall_status == Status.red.name:
                yield env.timeout(2)  # Κάθε 2 sec ελέγχει την πρώτη ύλη
                displayStop("Το Depall έχει τεθεί εκτός λειτουργίας (Status = RED).\n Αιτία: Φρακαρισμένη έξοδος.", env.now)
            else:
                yield env.timeout(2)  # Κάθε 2 sec ελέγχει την πρώτη ύλη

    def filler_batch_buffer(self):
        """Filler Batch. Στόχος: να μη σταματήσει ποτέ να λειτουργεί ο filler"""
        global filler_status, filler_description
        yield env.timeout(depall_ptime + filler_ptime + 4)

        while True:
            if self.depallCans.level < filler_critical_buffer:  # level < 1

                # Set Filler Buffer Status
                filler_status = Status.yellow.name
                filler_description = Status.yellow.value + ": Δεν υπάρχουν depallCan κουτιά για να γεμίσει (depall<1)"

                # print('%d: ' % env.now + '\x1b[0;30;46m' + 'Έναρξη εργασίας χειριστή.' + '\x1b[0m')
                print('%.2f: ' % env.now + 'Depall Can stock bellow critical level {0} cans at {1}'.format(self.depallCans.level, env.now))
                print('%.2f: ' % env.now + '\x1b[0;30;46m' + 'Filler: Ενημέρωση Συστήματος.' + '\x1b[0m')

                displayAlert("O Filler έχει τεθεί σε κατάσταση Stand By (Status = ORANGE).\n Αιτία: Δεν έχει 1 κουτί να εισάγει.", env.now)

                yield env.timeout(depall_ptime + 2)  # Περίμενε μέχρι να παράξει το Depall

                # print('%d: ' % env.now + '\x1b[0;30;46m' + 'Ο χειριστής Ενημερώθηκε!' + '\x1b[0m')
                yield env.timeout(1)
            else:
                yield env.timeout(1)  # Κάθε 1 sec ελέγχει την παραγωγή

    def pasteur_batch_buffer(self):
        """Pasteur Batch. O Pasteur πρέπει να παίρνει ανα 1..600 τα κουτιά"""
        global pasteur_status, pasteur_description
        yield env.timeout(depall_ptime + filler_ptime + 9)
        while True:
            # Pasteurize 1 to 600 cans
            if self.filledCans.level < pasteur_min_input:
                # Set Status
                pasteur_status = Status.yellow.name
                pasteur_description = Status.yellow.value
                print('%.2f: ' % env.now + '\x1b[0;30;46m' + 'Pasteur: Ενημέρωση Συστήματος.' + '\x1b[0m')
                print('%.2f: ' % env.now + 'Filled Cans stock = {0} bellow critical level < {1} at {2}'.format(
                    self.filledCans.level, pasteur_critical_buffer, env.now))

                displayAlert("O Pasteur έχει τεθεί σε κατάσταση Stand By (Status = ORANGE).\n Αιτία: Δεν έχει κουτιά να παράξει.", env.now)

                # Περίμενε μέχρι να παράξουν όλοι οι προηγούμενοι
                yield env.timeout(depall_ptime + filler_ptime + 9)

                yield env.timeout(1)
            else:
                yield env.timeout(depall_ptime + filler_ptime + 10)  # Κάθε x sec ελέγχει την παραγωγή


def depall():
    """Διεργασία του μηχανήματος Depall"""
    global depall_status, depall_description, current_depall_level
    while True:
        try:
            if can_pack_line.emptyCans.level >= depall_batch:
                yield env.timeout(0)  # Τα βάζει ακαριαία η μεταφορική RD

                print('%.2f: ' % env.now + Fore.BLUE + "Depall: ζητά {0} κουτιά για να επεξεργαστεί τη στιγμή {1}".format(depall_batch, env.now) + Fore.RESET)

                # παίρνει 500 cans απο τα emptyCan για να τα επεξεργαστεί (Process: Depalletization)
                yield can_pack_line.emptyCans.get(depall_input)
                print('%.2f: ' % env.now + Fore.BLUE + "Empty Cans Before proc: %d" % can_pack_line.emptyCans.level + Fore.RESET)
                print('%.2f: ' % env.now + Fore.BLUE + "Depall Cans Before Proc: %d" % can_pack_line.depallCans.level + Fore.RESET)

                # Τα παίρνει ανα παλέτα (5000) και τα βγάζει 1-1
                for i in range(depall_batch):
                    current_depall_level = depall_batch - i
                    # Set Depall Status
                    depall_status = Status.green.name
                    depall_description = Status.green.value

                    depall_total_ptime.append(depall_ptime)
                    # Επεξεργάζεται τα κουτιά για χρόνο ίσο με depall_ptime
                    yield env.timeout(depall_ptime)
                    yield can_pack_line.depallCans.put(depall_output)
                    print('%.2f: ' % env.now + Fore.BLUE + "Depalletized 1 can at {:.2f}".format(env.now) + Fore.RESET)

                # Βγάζει τα επεξεργασμένα cans και τα αποθηκεύσει στο depallCan
                print('%.2f: ' % env.now + Fore.BLUE + "Empty Cans After proc: %d" % can_pack_line.emptyCans.level + Fore.RESET)
                print('%.2f: ' % env.now + Fore.BLUE + "Depall Cans After Proc: %d" % can_pack_line.depallCans.level + Fore.RESET)

            else:
                yield env.timeout(1)
                # df.append({'ENV_NOW': env.now, 'Depall': 'ORANGE'}, ignore_index=True)

        except simpy.Interrupt:
            print("Depall has stopped")
            # broken = True

            # Set Depall Status
            depall_status = Status.red.name
            displayStop("Το Depall έχει τεθεί εκτός λειτουργίας (Status = RED).\n Αιτία: Φρακαρισμένη έξοδος.", env.now)

            # broken = False


def filler():
    """Διεργασία του μηχανήματος Filler"""
    global filler_status, filler_description, current_filler_level
    yield env.timeout(depall_ptime + 2)  # Ξεκινάει μετά απο Χ δευτερόλεπτα απο την έναρξη της παραγωγής

    while True:
        try:
            if can_pack_line.depallCans.level >= filler_batch:
                yield env.timeout(0)  # Τα βάζει ακαριαία η μεταφορική DF

                print('%.2f: ' % env.now + Fore.YELLOW + "Depall Cans Before proc: %d " % can_pack_line.depallCans.level + Fore.RESET)
                print('%.2f: ' % env.now + Fore.YELLOW + "Filled Cans Before proc: %d " % can_pack_line.filledCans.level + Fore.RESET)

                # Set Filler Status
                filler_status = Status.green.name
                filler_description = Status.green.value

                yield can_pack_line.depallCans.get(filler_input)
                filler_total_ptime.append(filler_ptime)
                yield env.timeout(filler_ptime)
                current_filler_level = filler_input
                print('%.2f: ' % env.now + Fore.YELLOW + "Filled 1 can at {:.2f}".format(env.now) + Fore.RESET)
                yield can_pack_line.filledCans.put(filler_output)

                print('%.2f: ' % env.now + Fore.YELLOW + "Depall Cans After Proc: %d" % can_pack_line.depallCans.level + Fore.RESET)
                print('%.2f: ' % env.now + Fore.YELLOW + "Filled Cans After proc: %d " % can_pack_line.filledCans.level + Fore.RESET)

            else:  # wait for product
                yield env.timeout(1)

        except simpy.Interrupt:
            print("Filler has stopped")
            # broken = True

            # Set Filler Status
            filler_status = Status.red.name
            displayStop("Ο Filler έχει τεθεί εκτός λειτουργίας (Status = RED).\n Αιτία: Φρακαρισμένη έξοδος.", env.now)

            # broken = False


threads = list()


def pasteur():
    """Διεργασία του μηχανήματος Pasteur"""
    global pasteur_status, pasteur_description, current_pasteur_level
    yield env.timeout(depall_ptime + filler_ptime + 4)

    while True:
        try:
            # Επεξεργάζεται όσα κουτιά και αν συναντήσει κάθε pasteur_batch_serve_time
            yield env.timeout(pasteur_batch_serve_time)
            if can_pack_line.filledCans.level >= pasteur_min_input:

                # Τα βάζει ακαριαία η μεταφορική FP
                print('%.2f: ' % env.now + Fore.LIGHTCYAN_EX + "Filled Cans Before proc: %d " % can_pack_line.filledCans.level + Fore.RESET)
                print('%.2f: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur: ζητά {0} κουτιά απο το Filler για να τα επεξεργαστεί τη στιγμή {1}".format(
                        can_pack_line.filledCans.level, round(env.now, 2)) + Fore.RESET)
                print('%.2f: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur Cans Before proc: %d " % can_pack_line.pastCans.level + Fore.RESET)

                # Set Pasteur Status
                pasteur_status = Status.green.name
                pasteur_description = Status.green.value

                # Πόσα κουτιά έχει σε κάθε batch - όσα βρίσκει παίρνει
                # if cans>batch input = batch else input= level
                if can_pack_line.filledCans.level >= pasteur_batch:
                    pasteur_input = pasteur_batch
                else:
                    pasteur_input = can_pack_line.filledCans.level

                print('%.2f: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur Input: %d " % pasteur_input + Fore.RESET)
                pasteur_total_ptime.append(pasteur_ptime)
                current_pasteur_level = pasteur_input

                # Pasteur Process
                def pasteur_process():
                    global current_pasteur_level
                    can_pack_line.filledCans.get(pasteur_input)
                    print("\nThread is starting\n")
                    env.timeout(pasteur_ptime)
                    pasteur_output = pasteur_input
                    can_pack_line.pastCans.put(pasteur_output)
                    print('%.2f: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur Cans After proc: %d " % can_pack_line.pastCans.level + Fore.RESET)
                    print('%.2f: ' % env.now + Fore.LIGHTCYAN_EX + "Filled Cans After Proc: %d " % can_pack_line.filledCans.level + Fore.RESET)

                t = threading.Thread(target=pasteur_process, name='t')
                t.start()
                threads.append(t)
                # t.join()
                # print(len(threads))

            else:
                # STATUS ORANGE
                yield env.timeout(2)
                print('%.2f: ' % env.now + Fore.LIGHTCYAN_EX + "Έχει κληθεί ο Pasteur Batch Buffer" + Fore.RESET)

        except simpy.Interrupt:
            print("Pasteur has stopped")
            # broken = True

            # Set Depall Status
            pasteur_status = Status.red.name
            displayStop("Ο Pasteur έχει τεθεί εκτός λειτουργίας (Status = RED).\n Αιτία: Φρακαρισμένη έξοδος.", env.now)

            # broken = False


def status_monitoring():
    """Παρακολούθηση μηχανών παραγωγής"""
    while True:
        global df, depall_status, filler_status, pasteur_status
        global depall_description, filler_description, pasteur_description

        yield env.timeout(DT)  # Κάθε χρόνο dt, εισάγει μια εγγραφή
        df = df.append({'ENV_NOW': env.now, 'Depall': depall_description, 'Filler': filler_description, 'Pasteur': pasteur_description},
                       ignore_index=True)

        write_row({'Env_now': env.now, 'Machine': 'Depall', 'Description': depall_description,
                   'Current_cans': can_pack_line.depallCans.level, 'Status': depall_status})
        write_row({'Env_now': env.now, 'Machine': 'Filler', 'Description': filler_description,
                   'Current_cans': can_pack_line.filledCans.level, 'Status': filler_status})
        write_row({'Env_now': env.now, 'Machine': 'Pasteur', 'Description': pasteur_description,
                   'Current_cans': can_pack_line.pastCans.level, 'Status': pasteur_status})


def live_monitoring():
    """Live Simulation Monitoring"""
    global current_depall_level, current_filler_level, current_pasteur_level

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
    pt = Label(window, bg='#6B8CD3', bd=4, height=2, justify=CENTER, relief=RAISED, text='Current Process Time: ' + str(round(env.now, 2)) + '  seconds', font="Arial 13 bold ")
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
        LB3 = Label(window, bg='#FAB3B3', bd=4, width=3, height=2, relief=RAISED)  # Red
        LB3.grid(row=1, column=col, padx=180, sticky=W)
        LB2 = Label(window, bg='#FBF3C1', bd=4, width=3, height=2, relief=RAISED)  # Yellow
        LB2.grid(row=2, column=col, padx=180, sticky=W)
        LB1 = Label(window, bg='#D9F2CC', bd=4, width=3, height=2, relief=RAISED)  # Green
        LB1.grid(row=3, column=col, padx=180, sticky=W)
        # Name
        Button(window, bg='#8DCDBA', bd=4, relief=RAISED, text=machine_name, font="Arial 13 bold").grid(row=3, column=col, padx=20, sticky=W)

        return LB3, LB2, LB1

    def current_conveyor_capacity_buffer(col, i_padx, current_level, machine_capacity, machine_description):
        """ Current level capacity status of conveyors """
        Label(window, text=machine_description, font="Arial 13", bg=window_colour, wraplength=140).grid(row=6, column=col, pady=0, sticky=S)
        Label(window, text=str(current_level) + ' / ' + str(machine_capacity), relief=RIDGE, font="Arial 15 bold", justify=CENTER).grid(row=7, column=col, ipadx=i_padx, ipady=15)

    def current_machine_buffer(col, i_padx, current_level, machine_capacity, machine_description):
        """ Current machine level capacity"""
        Label(window, text=machine_description, font="Arial 13", bg=window_colour).grid(row=6, column=col, pady=0, sticky=S)
        Label(window, text=str(current_level) + ' / ' + str(machine_capacity), relief=RIDGE, font="Arial 15 bold", justify=CENTER).grid(row=7, column=col, pady=0, ipadx=i_padx, ipady=15)

    def manual_brake(col, machine, repairers):
        """ Machine Brake Button """
        if MANUAL_BRAKE_VAR == 1:
            # Brake Button
            Button(window, text='BRAKE', command=partial(break_and_repair_machine, machine_name=machine, repairers=repairers), bg='#D97854', bd=4, font="Arial 13 bold", relief=RAISED, activebackground='#D97854').grid(row=5, column=col, sticky=W, pady=5, padx=100)
            # Repair Button
            Button(window, text='Repair', command=partial(break_and_repair_machine, machine_name=machine, repairers=repairers), bg='#86D954', bd=4, font="Arial 13 bold", relief=RAISED, activebackground='#86D954').grid(row=5, column=col, sticky=E, pady=5, padx=100)

    stop_dur = 30

    def kpis(col, run_times, run_duration, standby_times, standby_duration, stop_times, stop_duration):
        # Label
        Label(window, bg=window_colour, text='TIMES', font="Arial 15 bold").grid(row=10, column=col, sticky=W, padx=50)
        Label(window, bg=window_colour, text='DURATION', font="Arial 15 bold").grid(row=10, column=col, sticky=E, padx=80)
        # Run
        Label(window, bg='#9FE849', padx=30, relief=RIDGE, text=run_times, font="Arial 15 bold").grid(row=12, column=col, sticky=W, padx=50)
        Label(window, bg='#9FE849', padx=30, relief=RIDGE, text=run_duration, font="Arial 15 bold").grid(row=12, column=col, sticky=E, padx=60)
        Label(window, bg=window_colour, text=str(round(stop_dur, 2)) + ' %', font="Arial 15 bold").grid(row=12, column=col + 1, sticky=W)
        # Stand By
        Label(window, bg='#F5F372', padx=30, relief=RIDGE, text=standby_times, font="Arial 15 bold").grid(row=13, column=col, sticky=W, padx=50)
        Label(window, bg='#F5F372', padx=30, relief=RIDGE, text=standby_duration, font="Arial 15 bold").grid(row=13, column=col, sticky=E, padx=60)
        Label(window, bg=window_colour, text=str(round(stop_dur, 2)) + ' %', font="Arial 15 bold").grid(row=13, column=col + 1, sticky=W)
        # Stop
        Label(window, bg='#F57272', padx=30, relief=RIDGE, text=stop_times, font="Arial 15 bold").grid(row=14, column=col, sticky=W, padx=50, ipadx=5)
        Label(window, bg='#F57272', padx=30, relief=RIDGE, text=stop_duration, font="Arial 15 bold").grid(row=14, column=col, sticky=E, padx=60)
        Label(window, bg=window_colour, text=str(round(stop_dur, 2)) + ' %', font="Arial 15 bold").grid(row=14, column=col + 1, sticky=W)

    # Depall
    D_BL3, D_BL2, D_BL1 = machine_beacon(1, 'DEPALL')
    manual_brake(1, 'DEPALL', numOfRepairers)
    # Filler
    F_BL3, F_BL2, F_BL1 = machine_beacon(3, 'FILLER')
    manual_brake(3, 'FILLER', numOfRepairers)
    # Pasteur
    P_BL3, P_BL2, P_BL1 = machine_beacon(5, 'PASTEUR')
    manual_brake(5, 'PASTEUR', numOfRepairers)

    def beacon_status(status, BL3, BL2, BL1):
        if status == Status.green.name:
            BL3['bg'] = '#FAB3B3'
            BL2['bg'] = '#FBF3C1'
            BL1['bg'] = 'green'
        elif status == Status.yellow.name:
            BL3['bg'] = '#FAB3B3'
            BL2['bg'] = 'yellow'
            BL1['bg'] = '#D9F2CC'
        elif status == Status.red.name:
            BL3['bg'] = 'red'
            BL2['bg'] = '#FBF3C1'
            BL1['bg'] = '#D9F2CC'

    # Update
    def update():

        # Raw Material - Depall
        current_conveyor_capacity_buffer(0, 25, can_pack_line.emptyCans.level, depall_capacity, "Empty Cans / Conveyor C.")
        # Depall
        current_machine_buffer(1, 125, current_depall_level, depall_batch, "Current Process E-D / Depall Batch")
        kpis(1, '14', runTimeConv("Depall", depall_total_ptime, SHIFT), '3', '6h 30min', '3', '6h 30min')
        # Depall - Filler conveyor
        current_conveyor_capacity_buffer(2, 25, can_pack_line.depallCans.level, filler_capacity, "Depall Cans / Conveyor C.")
        # Filler
        current_machine_buffer(3, 135, current_filler_level, filler_batch, "Current Process D-F  / Filler Batch")
        kpis(3, '20', runTimeConv("Filler", filler_total_ptime, SHIFT), '5', '21h 30min', '5', '21h 30min')
        # Filler - Pasteur conveyor
        current_conveyor_capacity_buffer(4, 25, can_pack_line.filledCans.level, pasteur_capacity, "Filled Cans / Conveyor C.")
        # Pasteur
        current_machine_buffer(5, 115, current_pasteur_level, pasteur_batch, "Current Process F-P / Pasteur Batch")
        kpis(5, '5', runTimeConv("Pasteur", pasteur_total_ptime, SHIFT), '12', '19h 30min', '12', '19h 30min')
        # Pasteur - _  conveyor
        current_conveyor_capacity_buffer(6, 25, can_pack_line.pastCans.level, 'Inf', "Past Cans / Warehouse C.")

        beacon_status(depall_status, D_BL3, D_BL2, D_BL1)
        beacon_status(filler_status, F_BL3, F_BL2, F_BL1)
        beacon_status(pasteur_status, P_BL3, P_BL2, P_BL1)

        pt['text'] = 'Current Process Time: ' + str(round(env.now, 2)) + '  seconds'
        window.after(DT, update)

    update()

    # Close Button
    Button(window, text="Close", height=2, width=10, font="Arial 12 bold ", justify=CENTER, bd='5', bg='#479997',
           command=window.destroy).grid(row=15, columnspan=10, pady=40)

    window.resizable(True, True)
    window.mainloop()


# -------------------------------------------------
random.seed(RANDOM_SEED)  # Reproducing the results

# Environment Setup
env = simpy.Environment()
can_pack_line = CanPackLine()

threading.Thread(target=live_monitoring).start()


# Simulation
env.run(until=SIM_TIME)

print("\nTotal Production: " + str(can_pack_line.pastCans.level) + " beer cans in " + str(SHIFT) + " Shifts")
print("Expected Cans Production: {0} cans in {1} Shifts".format(cans_to_produce * SHIFT * 8, SHIFT))
print('Expected Simulation Duration: %d seconds\n' % SIM_TIME)
print('----------------------------------')
print('SIMULATION COMPLETED')
print('----------------------------------')
# gaussianPlot(PT_MEAN_depall, MTTF_depall)

# -------------------------------------------------
# ΜΕΤΡΙΚΕΣ / KPIs

print(df)
print("DF Len: ", len(df))
print("Times= ", int(times))

print('\x1b[1;30;45m' + 'ΜΕΤΡΙΚΕΣ / KPIs' + '\x1b[0m')

print("Pasteur function Calls: ", round(sum(pasteur_total_ptime)/SIM_TIME))
print("Threads: ", len(threads))

# -------------------------------------------------
# PLOTS
# Plot Gauss Graph
nums = []
for n in range(1000):
    tmp = random.gauss(mu=MU, sigma=SIGMA)
    nums.append(tmp)
plt.hist(nums, bins=200)
plt.show()

# Plot Uniform Graph
gfg = np.random.uniform(low=min_prob, high=max_prob, size=1000)
plt.hist(gfg, bins=50, density=True)
plt.show()
