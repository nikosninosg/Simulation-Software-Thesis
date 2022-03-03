import simpy
import random
import threading
import numpy as np
from enum import Enum
from OutputCSV import *
from Converters import *
from colorama import Fore
from WindowTkinter import *

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

# Ακρίβεια αποτελεσμάτων - παρακολούθησης | Ακρίβεια δευτερολέπτου
dt = 2000  # in seconds

# SIMULATION RUN TIME
SHIFT = 1  # Simulation time in shifts
SIM_TIME = SHIFT * 8 * 60 * 60  # Simulation time in seconds

times = SIM_TIME / dt  # Num of rows in csv

print("Simulation Time = %d seconds" % SIM_TIME)
# ---PRODUCTION---
cans_to_produce = 60000  # cans want to produce per hour
production_speed = round(cans_to_produce / 3600, 2)  # cans per second
print("Production Speed: {0} cans/second and: {1} cans/shift".format(production_speed, cans_to_produce * 8))

welcomeScreen()

print('----------------------------------')

# ---EMPTY CANS---
initial_emptyCans = 30000

# ---DEPALL---
# standard vars
depall_capacity = 50000  # 5000 = 1 παλέτα. Empty cans που μπορούν να περιμένουν μέχρι να επεξεργαστούν
initial_depallCans = 0  # Number αρχικών empty can που έχει το depall
depall_batch = 5000
depall_critical_buffer = depall_batch  # Παίρνει ανα 500 τα κουτιά για επεξεργασία = DEPALL BATCH
# dynamic vars
DEPALL_SPEED = production_speed  # cans / second
depall_input = depall_batch  # Πόσο προϊόν εισάγει για να επεξεργαστεί (input cans/sec)
depall_output = 1  # Πόσο προϊόν εξάγει μετά την επεξεργασία (output cans/sec)
depall_ptime = depall_output / DEPALL_SPEED  # Depall Process Time
MTBF_depall = 31.03  # standard error se min (MTTF)
# status
depall_status = "STAND BY"
depall_description = "Έναρξη παραγωγής"

# ---FILLER---
# standard vars
filler_capacity = 4000  # Depalletized cans που μπορούν να περιμένουν μέχρι να επεξεργαστούν
initial_filledCans = 0  # Number αρχικών depall can που έχει ο filler
filler_batch = 1
filler_critical_buffer = filler_batch
# dynamic vars
FILLER_SPEED = production_speed  # cans / second
filler_input = filler_batch  # Πόσο προϊόν εισάγει για να επεξεργαστεί (input cans/sec)
filler_output = filler_input  # Πόσο προϊόν εξάγει μετά την επεξεργασία (output cans/sec)
filler_ptime = filler_output / FILLER_SPEED  # Filler Process Time
MTBF_filler = 5.34  # standard error se min (MTTF)
# status
filler_status = "STAND BY"
filler_description = "Έναρξη παραγωγής"

# ---PASTEUR---
# standard vars
pasteur_capacity = 2000  # Filled cans που μπορούν να περιμένουν μέχρι να επεξεργαστούν
initial_pastCans = 0  # Number αρχικών Filled can που έχει ο Pasteur
pasteur_batch = 600
pasteur_critical_buffer = pasteur_batch
# dynamic vars
# PASTEUR_SPEED =  # cans / second
pasteur_min_input = 1  # Πόσο προϊόν εισάγει για να επεξεργαστεί (input cans/sec)
pasteur_batch_serve_time = 30  # seconds
# pasteur_output = pasteur_input  # Πόσο προϊόν εξάγει μετά την επεξεργασία (output cans/sec)
pasteur_ptime = 1800  # Pasteur Process Time 30 minutes
MTBF_pasteur = 25.22  # standard error se min (MTTF)
# status
pasteur_status = "STAND BY"
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
    orange = "STAND BY"
    red = "STOP"


def break_and_repair_machine(machine, repairers):
    """Εντοπισμός σταματήματος σε μηχάνημα και έναρξη εργασίας επισκευής μηχανήματος"""
    global depall_status, filler_status, pasteur_status
    if np.random.uniform(low=min_prob, high=max_prob) == 2:  # probability 1/30000
        # Set Status
        if machine == 'Depall':
            depall_status = Status.red.value
        elif machine == 'Filler':
            filler_status = Status.red.value
        elif machine == 'Pasteur':
            pasteur_status = Status.red.value

        print('%d: ' % env.now + "Breakdown Detected in Machine: " + machine)
        yield env.timeout(1)
        print('%d: ' % env.now + "Repair of Machine: " + machine + " Started")
        with repairers.request() as request:
            yield request
            rep_time = random.gauss(mu=MU, sigma=SIGMA)
            yield env.timeout(rep_time)

        print('%d: ' % env.now + "Repair of Machine: " + machine + " Completed After: %f minutes" % rep_time)


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
        self.emptyCan = simpy.Container(env, capacity=depall_capacity, init=initial_emptyCans)

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
        self.monitor_gen = env.process(status_monitoring())

    def depall_can_stock_control(self):
        """Depall Batch: Δεν πρέπει να πέσει κάτω απο depall_batch κουτιά για να μη σταματήσει να λειτουργεί"""
        global depall_status, depall_description
        yield env.timeout(0)

        while True:
            if self.emptyCan.level <= depall_critical_buffer:  # level < 5000

                # Set Depall Buffer Status
                depall_status = Status.orange.value
                depall_description = "Το επίπεδο άδειων κουτιών είναι κάτω απο το όριο. (empty < 5000)"

                print('%.2f: ' % env.now + '\x1b[0;30;44m' + 'Έναρξη Εισαγωγής Παλέτας.' + '\x1b[0m')
                print('%.2f: ' % env.now + 'Empty Cans level = {0}'.format(self.emptyCan.level))
                print('%.2f: ' % env.now + "Προστέθηκαν %d παλεταρισμένα κουτιά." % depall_input)

                yield env.timeout(0)  # Εργασία χειριστή
                # displayAlert(
                #    "Το Depall έχει τεθεί σε κατάσταση Stand By (Status = ORANGE).\n Αιτία: Έχει πέσει κάτω απο 5.000 κουτιά.", env.now)

                # Pall cans που πρόσθεσε ο χειριστής ως πρώτη ύλη στο depall
                yield can_pack_line.emptyCan.put(depall_input)
                print('%.2f: ' % env.now + 'New empty cans stock is {0}'.format(self.emptyCan.level))
                print('%.2f: ' % env.now + '\x1b[0;30;44m' + 'Τέλος Εισαγωγής παλέτας' + '\x1b[0m')
            else:
                yield env.timeout(2)  # Κάθε 2 sec ελέγχει την πρώτη ύλη

    def filler_batch_buffer(self):
        """Filler Batch. Στόχος: να μη σταματήσει ποτέ να λειτουργεί ο filler"""
        global filler_status, filler_description
        yield env.timeout(depall_ptime + filler_ptime + 4)

        while True:
            if self.depallCans.level < filler_critical_buffer:  # level < 1

                # Set Filler Buffer Status
                filler_status = Status.orange.value
                filler_description = "Δεν υπάρχουν depallCan κουτιά για να γεμίσει (depall<1)"

                # print('%d: ' % env.now + '\x1b[0;30;46m' + 'Έναρξη εργασίας χειριστή.' + '\x1b[0m')
                print('%.2f: ' % env.now + 'Depall Can stock bellow critical level {0} cans at {1}'.format(
                    self.depallCans.level, env.now))
                print('%.2f: ' % env.now + '\x1b[0;30;46m' + 'Filler: Ενημέρωση Συστήματος.' + '\x1b[0m')

                displayAlert(
                    "O Filler έχει τεθεί σε κατάσταση Stand By (Status = ORANGE).\n Αιτία: Δεν έχει 1 κουτί να εισάγει.", env.now)

                yield env.timeout(depall_ptime + 2)  # Περίμενε μέχρι να παράξει το Depall

                # print('%d: ' % env.now + '\x1b[0;30;46m' + 'Ο χειριστής Ενημερώθηκε!' + '\x1b[0m')
                yield env.timeout(1)
            else:
                yield env.timeout(1)  # Κάθε 1 sec ελέγχει την παραγωγή

    def pasteur_batch_buffer(self):
        """Pasteur Batch. O Pasteur πρέπει να παίρνει ανα 1..600 τα κουτιά"""
        global pasteur_status
        yield env.timeout(depall_ptime + filler_ptime + 9)
        while True:
            # Pasteurize 1 to 600 cans
            if self.filledCans.level < pasteur_min_input:
                # Set Status
                pasteur_status = Status.orange.value
                print('%.2f: ' % env.now + '\x1b[0;30;46m' + 'Pasteur: Ενημέρωση Συστήματος.' + '\x1b[0m')
                print('%.2f: ' % env.now + 'Filled Cans stock = {0} bellow critical level < {1} at {2}'.format(
                    self.filledCans.level, pasteur_critical_buffer, env.now))

                displayAlert(
                    "O Pasteur έχει τεθεί σε κατάσταση Stand By (Status = ORANGE).\n Αιτία: Δεν έχει κουτιά να παράξει.", env.now)

                # Περίμενε μέχρι να παράξουν όλοι οι προηγούμενοι
                yield env.timeout(depall_ptime + filler_ptime + 9)

                yield env.timeout(1)
            else:
                yield env.timeout(depall_ptime + filler_ptime + 10)  # Κάθε x sec ελέγχει την παραγωγή


def depall():
    """Διεργασία του μηχανήματος Depall"""
    global depall_status, depall_description
    while True:
        if can_pack_line.emptyCan.level >= depall_batch:
            yield env.timeout(0)  # Τα βάζει ακαριαία η μεταφορική RD

            print(
                '%.2f: ' % env.now + Fore.BLUE + "Depall: ζητά {0} κουτιά για να επεξεργαστεί τη στιγμή {1}".format(
                    depall_batch, env.now) + Fore.RESET)

            # παίρνει 500 cans απο τα emptyCan για να τα επεξεργαστεί (Process: Depalletization)
            yield can_pack_line.emptyCan.get(depall_input)
            print(
                '%.2f: ' % env.now + Fore.BLUE + "Empty Cans Before proc: %d" % can_pack_line.emptyCan.level + Fore.RESET)
            print(
                '%.2f: ' % env.now + Fore.BLUE + "Depall Cans Before Proc: %d" % can_pack_line.depallCans.level + Fore.RESET)

            # Τα παίρνει ανα παλέτα (5000) και τα βγάζει 1-1
            for i in range(depall_batch):
                # Set Depall Status
                depall_status = Status.green.value
                depall_description = 'Processing'

                depall_total_ptime.append(depall_ptime)
                # Επεξεργάζεται τα κουτιά για χρόνο ίσο με depall_ptime
                yield env.timeout(depall_ptime)
                yield can_pack_line.depallCans.put(depall_output)
                print('%.2f: ' % env.now + Fore.BLUE + "Depalletized 1 can at {:.2f}".format(env.now) + Fore.RESET)

            # Βγάζει τα επεξεργασμένα cans και τα αποθηκεύσει στο depallCan
            print(
                '%.2f: ' % env.now + Fore.BLUE + "Empty Cans After proc: %d" % can_pack_line.emptyCan.level + Fore.RESET)
            print(
                '%.2f: ' % env.now + Fore.BLUE + "Depall Cans After Proc: %d" % can_pack_line.depallCans.level + Fore.RESET)

        else:
            yield env.timeout(1)
            # df.append({'ENV_NOW': env.now, 'Depall': 'ORANGE'}, ignore_index=True)


def filler():
    """Διεργασία του μηχανήματος Filler"""
    global filler_status, filler_description
    yield env.timeout(depall_ptime + 2)  # Ξεκινάει μετά απο Χ δευτερόλεπτα απο την έναρξη της παραγωγής

    while True:
        if can_pack_line.depallCans.level >= filler_batch:
            yield env.timeout(0)  # Τα βάζει ακαριαία η μεταφορική DF

            print(
                '%.2f: ' % env.now + Fore.YELLOW + "Depall Cans Before proc: %d " % can_pack_line.depallCans.level + Fore.RESET)
            print(
                '%.2f: ' % env.now + Fore.YELLOW + "Filled Cans Before proc: %d " % can_pack_line.filledCans.level + Fore.RESET)

            # Set Filler Status
            filler_status = Status.green.value
            filler_description = 'Processing'

            yield can_pack_line.depallCans.get(filler_input)

            filler_total_ptime.append(filler_ptime)
            yield env.timeout(filler_ptime)
            print(
                '%.2f: ' % env.now + Fore.YELLOW + "Filled 1 can at {:.2f}".format(env.now) + Fore.RESET)
            yield can_pack_line.filledCans.put(filler_output)

            print(
                '%.2f: ' % env.now + Fore.YELLOW + "Depall Cans After Proc: %d" % can_pack_line.depallCans.level + Fore.RESET)
            print(
                '%.2f: ' % env.now + Fore.YELLOW + "Filled Cans After proc: %d " % can_pack_line.filledCans.level + Fore.RESET)

        else:  # wait for product
            # df.append({'ENV_NOW': env.now, 'Filler': 'ORANGE'}, ignore_index=True)
            yield env.timeout(1)


threads = list()


def pasteur():
    """Διεργασία του μηχανήματος Pasteur"""
    global pasteur_status, pasteur_description
    yield env.timeout(depall_ptime + filler_ptime + 4)

    while True:
        # Επεξεργάζεται όσα κουτιά και αν συναντήσει κάθε pasteur_batch_serve_time
        yield env.timeout(pasteur_batch_serve_time)
        if can_pack_line.filledCans.level >= pasteur_min_input:

            # Τα βάζει ακαριαία η μεταφορική FP
            print(
                '%.2f: ' % env.now + Fore.LIGHTCYAN_EX + "Filled Cans Before proc: %d " % can_pack_line.filledCans.level + Fore.RESET)
            print(
                '%.2f: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur: ζητά {0} κουτιά απο το Filler για να τα επεξεργαστεί τη στιγμή {1}".format(
                    can_pack_line.filledCans.level, round(env.now, 2)) + Fore.RESET)
            print(
                '%.2f: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur Cans Before proc: %d " % can_pack_line.pastCans.level + Fore.RESET)

            # Set Pasteur Status
            pasteur_status = Status.green.value
            pasteur_description = 'Processing'

            # Πόσα κουτιά έχει σε κάθε batch - όσα βρίσκει παίρνει
            # if cans>batch input = batch else input= level
            if can_pack_line.filledCans.level >= pasteur_batch:
                pasteur_input = pasteur_batch
            else:
                pasteur_input = can_pack_line.filledCans.level

            print('%.2f: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur Input: %d " % pasteur_input + Fore.RESET)
            pasteur_total_ptime.append(pasteur_ptime)

            # Pasteur Process
            def pasteur_process():
                can_pack_line.filledCans.get(pasteur_input)
                print("\nThread is starting\n")
                env.timeout(pasteur_ptime)
                pasteur_output = pasteur_input
                can_pack_line.pastCans.put(pasteur_output)
                print(
                    '%.2f: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur Cans After proc: %d " % can_pack_line.pastCans.level + Fore.RESET)
                print(
                    '%.2f: ' % env.now + Fore.LIGHTCYAN_EX + "Filled Cans After Proc: %d " % can_pack_line.filledCans.level + Fore.RESET)

            t = threading.Thread(target=pasteur_process, name='t')
            t.start()
            threads.append(t)
            # t.join()
            print(len(threads))

        else:
            # STATUS ORANGE
            yield env.timeout(2)
            print('%.2f: ' % env.now + Fore.LIGHTCYAN_EX + "Έχει κληθεί ο Pasteur Batch Buffer" + Fore.RESET)


def status_monitoring():
    """Παρακολούθηση μηχανών παραγωγής"""
    while True:
        global df, depall_status, filler_status, pasteur_status
        global depall_description, filler_description, pasteur_description

        yield env.timeout(dt)  # Κάθε χρόνο dt, εισάγει μια εγγραφή

        df = df.append({'ENV_NOW': env.now, 'Depall': depall_status, 'Filler': filler_status, 'Pasteur': pasteur_status},
                       ignore_index=True)

        write_row({'Env_now': env.now, 'Machine': 'Depall', 'Description': depall_description,
                   'Current_cans': can_pack_line.depallCans.level, 'Status': depall_status})
        write_row({'Env_now': env.now, 'Machine': 'Filler', 'Description': filler_description,
                   'Current_cans': can_pack_line.filledCans.level, 'Status': filler_status})
        write_row({'Env_now': env.now, 'Machine': 'Pasteur', 'Description': pasteur_description,
                   'Current_cans': can_pack_line.pastCans.level, 'Status': pasteur_status})


import random
from tkinter import *
from enum import Enum


class Status(Enum):
    GREEN = "green"
    ORANGE = "orange"
    RED = "red"


dt = 1000


def liveMonitoring(status1, status2, status3, current_ptime):
    window = Tk()

    # if window.state == 'normal':
    #    window.destroy()

    window.title("Live Process Monitoring!")

    current_ptime = str(current_ptime)

    window.geometry('1400x600')

    # canvas = Canvas(window)
    # canvas.grid(row=1, column=1 & 2)

    # Depall
    l1 = Label(bg=status1, bd=4, height=7, justify=LEFT, padx=100, relief=RAISED, text='Depall', font="Arial 15 bold ")
    l1.grid(row=1, column=0, padx=100, sticky=W)

    # line x0, y0, x1, y1
    # canvas.create_line(320, 130, 600, 130)
    # canvas.grid(row=1)
    # canvas.create_line(0, 130, 200, 130)
    # canvas.grid(row=1, column=1)

    # Filler
    l2 = Label(bg=status2, bd=4, height=7, justify=CENTER, padx=100, relief=RAISED, text='Filler',
               font="Arial 15 bold ")
    l2.grid(row=1, column=1, padx=100, pady=30, sticky=N)

    # Pasteur
    l3 = Label(bg=status3, bd=4, height=7, justify=LEFT, padx=100, relief=RAISED, text='Pasteur', font="Arial 15 bold ")
    l3.grid(row=1, column=2, padx=100, sticky=E)

    # Current Process Time
    pt = Label(bg='#DCDCDC', bd=4, height=2, justify=CENTER, relief=SUNKEN,
               text='Current Process Time: ' + current_ptime + '  minutes', font="Arial 13 bold ")
    pt.grid(row=2, column=1, pady=70)
    foo = ['green', 'blue', 'yellow', 'orange']

    # Update
    def update():
        l1['bg'] = random.choice(foo)
        l2['bg'] = random.choice(foo)
        l3['bg'] = random.choice(foo)
        pt['text'] = 'Current Process Time: ' + current_ptime + '  minutes'
        window.after(dt, update)

    update()

    # Close Button
    Button(window, text="Close", height=2, width=10, font="Arial 12 bold ", justify=CENTER, bd='5', bg='#479997',
           command=window.destroy).grid(row=4, column=1, pady=70)
    # print(window.state)
    window.mainloop()


# Test Code
lis = [Status.GREEN, Status.ORANGE, Status.RED]

for x in range(1, 10):
    liveMonitoring(random.choice(lis).value, random.choice(lis).value, random.choice(lis).value, x)


# -------------------------------------------------
random.seed(RANDOM_SEED)  # Reproducing the results

# Environment Setup
env = simpy.Environment()
can_pack_line = CanPackLine()

# Simulation
env.run(until=SIM_TIME)

print("\nTotal Production: " + str(can_pack_line.pastCans.level) + " beer cans in " + str(
    SHIFT) + " Shifts")
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
processTimeConv("Depall", depall_total_ptime, SHIFT)
processTimeConv("Filler", filler_total_ptime, SHIFT)
processTimeConv("Pasteur", pasteur_total_ptime, SHIFT)
print("Pasteur function Calls: ", round(sum(pasteur_total_ptime)/SIM_TIME))
print("Threads: ", len(threads))

# Plot Gauss
nums = []
for n in range(1000):
    tmp = random.gauss(mu=MU, sigma=SIGMA)
    nums.append(tmp)

# Plot Gauss Graph
plt.hist(nums, bins=200)
plt.show()

# Plot Uniform Graph
gfg = np.random.uniform(low=min_prob, high=max_prob, size=1000)
plt.hist(gfg, bins=50, density=True)
plt.show()
