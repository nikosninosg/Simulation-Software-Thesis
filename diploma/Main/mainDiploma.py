import simpy
import random
import threading
import numpy as np
from enum import Enum
from OutputCSV import *
from colorama import Fore
from WindowTkinter import *
from functools import partial
# import matplotlib.pyplot as plt

# matplotlib.use('Agg')

cans_produced = 0  # Συνολικά παραγμένα κουτιά


print('----------------------------------')
print("STARTING SIMULATION")

# Αδειάζει το csv για να γράψει τις νέες τιμές
check_csv()

# -------------------------------------------------

# Parameters
# DEPALL_BRAKE_PROB, FILLER_BRAKE_PROB, PASTEUR_BRAKE_PROB, AUTO_BRAKE_VAR, HOURS, DT = welcomeScreen()
AUTO_BRAKE_VAR = 1
# Ακρίβεια αποτελεσμάτων - παρακολούθησης | Ακρίβεια δευτερολέπτου
DT = 200  # in seconds

# SIMULATION RUN TIME
HOURS = 16  # Simulation time in shifts
SIM_TIME = HOURS * 60 * 60  # Simulation time in seconds

times = SIM_TIME / DT  # Num of rows in csv

print("Simulation Time = %d seconds" % SIM_TIME)
# ---PRODUCTION---
CANS_PER_HOUR = 60000  # cans want to produce per hour
PRODUCTION_SPEED = round(CANS_PER_HOUR / 3600, 2)  # cans per second
print("Production Speed: {0} cans/second and: {1} cans/shift".format(PRODUCTION_SPEED, CANS_PER_HOUR * 8))


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
DEPALL_SPEED = PRODUCTION_SPEED  # cans / second
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
FILLER_SPEED = PRODUCTION_SPEED  # cans / second
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

# --- RCA VARIABLES ---
# Depall
VAR_STOP_D = True
DEPALL_IS_BROKEN = False
DEPALL_RUN_DURATION = {}
DEPALL_RUN_TIMES = 1
DEPALL_STANDBY_DURATION = {}
DEPALL_STANDBY_TIMES = 0
DEPALL_STOP_DURATION = {}
DEPALL_STOP_TIMES = 0

# Filler
VAR_STOP_F = True
FILLER_IS_BROKEN = False
FILLER_RUN_DURATION = {}
FILLER_RUN_TIMES = 1
FILLER_STANDBY_DURATION = {}
FILLER_STANDBY_TIMES = 0
FILLER_STOP_DURATION = {}
FILLER_STOP_TIMES = 0

# Pasteur
VAR_STOP_P = True
PASTEUR_IS_BROKEN = False
PASTEUR_RUN_DURATION = {}
PASTEUR_RUN_TIMES = 1
PASTEUR_STANDBY_DURATION = {}
PASTEUR_STANDBY_TIMES = 0
PASTEUR_STOP_DURATION = {}
PASTEUR_STOP_TIMES = 0

# ---Machine Breakdown---
# Breakdown Probability
MIN_PROB = 1
MAX_PROB = 1000
# Repair Time = Gauss Distribution
MU = 15
SIGMA = 5

# ---GENERAL VARIABLES---

RANDOM_SEED = 42  # Reproduce the results

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


DEPALL_BRAKE_PROB = FILLER_BRAKE_PROB = PASTEUR_BRAKE_PROB = 10


def auto_brake_machine():
    """ Automated Breakdown Function with probability """
    global DEPALL_IS_BROKEN, FILLER_IS_BROKEN, PASTEUR_IS_BROKEN

    if AUTO_BRAKE_VAR == 1:
        print("Auto breakdown mode enabled")
        while True:
            # CHECK PERIOD
            yield env.timeout(100)
            # Depall Brake Probability
            if np.random.binomial(1, DEPALL_BRAKE_PROB/100) == 1 and not DEPALL_IS_BROKEN:
                DEPALL_IS_BROKEN = True
                can_pack_line.depall_gen.interrupt()
                print("Inside def probability, Depall")

            # Filler Brake Probability
            if np.random.binomial(1, FILLER_BRAKE_PROB / 100) == 1 and not FILLER_IS_BROKEN:
                FILLER_IS_BROKEN = True
                can_pack_line.filler_gen.interrupt()
                print("Inside def probability, Filler")

            # Pasteur Brake Probability
            if np.random.binomial(1, PASTEUR_BRAKE_PROB/100) == 1 and not PASTEUR_IS_BROKEN:
                PASTEUR_IS_BROKEN = True
                can_pack_line.pasteur_gen.interrupt()
                print("Inside def probability, Pasteur")


def manual_break_and_repair_machine(machine_name):
    """Εντοπισμός σταματήματος σε μηχάνημα και έναρξη εργασίας επισκευής μηχανήματος"""
    global depall_status, filler_status, pasteur_status

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
    env.timeout(1)  # 1 time unit to detect breakdown


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

        # MAIN PROCESS DECLARE & STARTUP
        self.depall_gen = env.process(depall())
        self.filler_gen = env.process(filler())
        self.pasteur_gen = env.process(pasteur())
        self.status_monitoring_gen = env.process(status_monitoring())

        # Automated Breakdown
        self.auto_brake_machine_gen = env.process(auto_brake_machine())

    def depall_can_stock_control(self):
        """Depall Batch: Δεν πρέπει να πέσει κάτω απο depall_batch κουτιά για να μη σταματήσει να λειτουργεί"""
        global depall_status, depall_description, DEPALL_STANDBY_TIMES, DEPALL_STANDBY_DURATION
        yield env.timeout(0)

        while True:
            if self.emptyCans.level <= depall_critical_buffer:  # level < 5000
                depall_standby_start = env.now
                # Set Depall Buffer Status
                DEPALL_STANDBY_TIMES += 1
                depall_status = Status.yellow.name
                depall_description = Status.yellow.value

                print('%.2f: ' % env.now + '\x1b[0;30;44m' + 'Έναρξη Εισαγωγής Παλέτας.' + '\x1b[0m')
                print('%.2f: ' % env.now + 'Empty Cans level = {0}'.format(self.emptyCans.level))
                print('%.2f: ' % env.now + "Προστέθηκαν %d παλεταρισμένα κουτιά." % depall_input)

                yield env.timeout(0)  # Εργασία χειριστή
                # displayAlert("Το Depall έχει τεθεί σε κατάσταση Stand By (Status = ORANGE).\n Αιτία: Έχει πέσει κάτω απο 5.000 κουτιά.", env.now)

                # Pall cans που πρόσθεσε ο χειριστής ως πρώτη ύλη στο depall
                yield can_pack_line.emptyCans.put(depall_input)
                print('%.2f: ' % env.now + 'New empty cans stock is {0}'.format(self.emptyCans.level))
                print('%.2f: ' % env.now + '\x1b[0;30;44m' + 'Τέλος Εισαγωγής παλέτας' + '\x1b[0m')
                depall_standby_finish = env.now
                DEPALL_STANDBY_DURATION[DEPALL_STANDBY_TIMES] = depall_standby_finish - depall_standby_start

            else:
                yield env.timeout(2)  # Κάθε 2 sec ελέγχει την πρώτη ύλη

    def filler_batch_buffer(self):
        """Filler Batch. Στόχος: να μη σταματήσει ποτέ να λειτουργεί ο filler"""
        global filler_status, filler_description, FILLER_STANDBY_TIMES, FILLER_STANDBY_DURATION
        yield env.timeout(depall_ptime + filler_ptime + 4)

        while True:
            if self.depallCans.level < filler_critical_buffer:  # level < 1
                filler_standby_start = env.now
                FILLER_STANDBY_TIMES += 1

                # Set Filler Buffer Status
                filler_status = Status.yellow.name
                filler_description = Status.yellow.value   # + ": Δεν υπάρχουν depallCan κουτιά για να γεμίσει (depall<1)"

                # print('%d: ' % env.now + '\x1b[0;30;46m' + 'Έναρξη εργασίας χειριστή.' + '\x1b[0m')
                print('%.2f: ' % env.now + 'Depall Can stock bellow critical level {0} cans at {1}'.format(self.depallCans.level, env.now))
                print('%.2f: ' % env.now + '\x1b[0;30;46m' + 'Filler: Ενημέρωση Συστήματος.' + '\x1b[0m')

                # displayAlert("O Filler έχει τεθεί σε κατάσταση Stand By (Status = ORANGE).\n Αιτία: Δεν έχει 1 κουτί να εισάγει.", env.now)

                yield env.timeout(depall_ptime + 2)  # Περίμενε μέχρι να παράξει το Depall

                # print('%d: ' % env.now + '\x1b[0;30;46m' + 'Ο χειριστής Ενημερώθηκε!' + '\x1b[0m')
                yield env.timeout(1)
                filler_standby_finish = env.now
                FILLER_STANDBY_DURATION[FILLER_STANDBY_TIMES] = filler_standby_finish - filler_standby_start

            else:
                yield env.timeout(1)  # Κάθε 1 sec ελέγχει την παραγωγή

    def pasteur_batch_buffer(self):
        """Pasteur Batch. O Pasteur πρέπει να παίρνει ανα 1..600 τα κουτιά"""
        global pasteur_status, pasteur_description, PASTEUR_STANDBY_TIMES, PASTEUR_STANDBY_DURATION
        yield env.timeout(depall_ptime + filler_ptime + 9)
        while True:
            # Pasteurize 1 to 600 cans
            if self.filledCans.level < pasteur_min_input:
                # Set Status
                pasteur_status = Status.yellow.name
                pasteur_description = Status.yellow.value

                pasteur_standby_start = env.now
                PASTEUR_STANDBY_TIMES += 1

                print('%.2f: ' % env.now + '\x1b[0;30;46m' + 'Pasteur: Ενημέρωση Συστήματος.' + '\x1b[0m')
                print('%.2f: ' % env.now + 'Filled Cans stock = {0} bellow critical level < {1} at {2}'.format(
                    self.filledCans.level, pasteur_critical_buffer, env.now))

                # displayAlert("O Pasteur έχει τεθεί σε κατάσταση Stand By (Status = ORANGE).\n Αιτία: Δεν έχει κουτιά να παράξει.", env.now)

                # Περίμενε μέχρι να παράξουν όλοι οι προηγούμενοι
                # yield env.timeout(depall_ptime + filler_ptime + 9)
                if self.filledCans.level > 1:
                    # Production Started
                    pasteur_standby_finish = env.now
                    pass
                else:
                    # Wait until find product
                    pasteur_standby_finish = env.now

                yield env.timeout(1)
                PASTEUR_STANDBY_DURATION[PASTEUR_STANDBY_TIMES] = pasteur_standby_finish - pasteur_standby_start
            else:
                yield env.timeout(depall_ptime + filler_ptime + 4)  # Κάθε x sec ελέγχει την παραγωγή


def depall():
    """Διεργασία του μηχανήματος Depall"""
    global depall_status, depall_description, current_depall_level
    global VAR_STOP_D, DEPALL_RUN_TIMES, DEPALL_RUN_DURATION, DEPALL_STOP_TIMES, DEPALL_STOP_DURATION, DEPALL_IS_BROKEN
    while True:
        try:
            if can_pack_line.emptyCans.level >= depall_batch and not DEPALL_IS_BROKEN:
                yield env.timeout(0.01)  # Τα βάζει ακαριαία η μεταφορική RD
                depall_status = Status.green.name
                depall_description = Status.green.value
                DEPALL_RUN_TIMES += 1
                depall_run_start = env.now

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

                    # DEPALL_RUN_DURATION.append(depall_ptime)
                    # Επεξεργάζεται τα κουτιά για χρόνο ίσο με depall_ptime
                    yield env.timeout(depall_ptime)
                    yield can_pack_line.depallCans.put(depall_output)
                    print('%.2f: ' % env.now + Fore.BLUE + "Depalletized 1 can at {:.2f}".format(env.now) + Fore.RESET)

                # Βγάζει τα επεξεργασμένα cans και τα αποθηκεύσει στο depallCan
                print('%.2f: ' % env.now + Fore.BLUE + "Empty Cans After proc: %d" % can_pack_line.emptyCans.level + Fore.RESET)
                print('%.2f: ' % env.now + Fore.BLUE + "Depall Cans After Proc: %d" % can_pack_line.depallCans.level + Fore.RESET)

                depall_run_finish = env.now
                DEPALL_RUN_DURATION[DEPALL_RUN_TIMES] = depall_run_finish - depall_run_start

            else:
                yield env.timeout(1)

        except simpy.Interrupt:
            yield env.timeout(0.01)
            print("Depall has stopped")
            start_depall_break = env.now
            depall_status = Status.red.name
            depall_description = Status.red.value
            DEPALL_STOP_TIMES += 1

            # Manual Breakdown
            if AUTO_BRAKE_VAR == 0:
                while VAR_STOP_D:
                    # Set Depall Status
                    yield env.timeout(0.01)
                    depall_status = Status.red.name
                    depall_description = Status.red.value

                VAR_STOP_D = True

            # Automated Breakdown
            else:
                # Brake Duration. (Repair After 5-30 min)
                repair_at = start_depall_break + random.uniform(300, 1800)

                while env.now <= repair_at:
                    yield env.timeout(0.01)
                    depall_status = Status.red.name
                    depall_description = Status.red.value
                    # yield env.timeout(random.uniform(300, 1800))

                DEPALL_IS_BROKEN = False

            # displayStop("Το Depall έχει τεθεί εκτός λειτουργίας (Status = RED).\n Αιτία: Φρακαρισμένη έξοδος.", env.now)
            finish_depall_break = env.now
            DEPALL_STOP_DURATION[DEPALL_STOP_TIMES] = finish_depall_break - start_depall_break


def filler():
    """Διεργασία του μηχανήματος Filler"""
    global filler_status, filler_description, current_filler_level
    global VAR_STOP_F, FILLER_RUN_TIMES, FILLER_RUN_DURATION, FILLER_STOP_TIMES, FILLER_STOP_DURATION, FILLER_IS_BROKEN
    yield env.timeout(depall_ptime + 2)  # Ξεκινάει μετά απο Χ δευτερόλεπτα απο την έναρξη της παραγωγής

    while True:
        try:
            if not FILLER_IS_BROKEN:
                yield env.timeout(0)  # Τα βάζει ακαριαία η μεταφορική DF
                filler_run_start = env.now
                FILLER_RUN_TIMES += 1

                print('%.2f: ' % env.now + Fore.YELLOW + "Depall Cans Before proc: %d " % can_pack_line.depallCans.level + Fore.RESET)
                print('%.2f: ' % env.now + Fore.YELLOW + "Filled Cans Before proc: %d " % can_pack_line.filledCans.level + Fore.RESET)

                # Set Filler Status
                filler_status = Status.green.name
                filler_description = Status.green.value

                yield can_pack_line.depallCans.get(filler_input)
                yield env.timeout(filler_ptime)
                if can_pack_line.depallCans.level >= filler_batch:
                    current_filler_level = filler_input
                else:
                    current_filler_level = 0
                    yield can_pack_line.filledCans.put(1)
                print('%.2f: ' % env.now + Fore.YELLOW + "Filled 1 can at {:.2f}".format(env.now) + Fore.RESET)
                yield can_pack_line.filledCans.put(filler_output)

                print('%.2f: ' % env.now + Fore.YELLOW + "Depall Cans After Proc: %d" % can_pack_line.depallCans.level + Fore.RESET)
                print('%.2f: ' % env.now + Fore.YELLOW + "Filled Cans After proc: %d " % can_pack_line.filledCans.level + Fore.RESET)

                filler_run_finish = env.now
                FILLER_RUN_DURATION[FILLER_RUN_TIMES] = filler_run_finish - filler_run_start

        except simpy.Interrupt:
            yield env.timeout(0)
            print("Filler has stopped")
            start_filler_break = env.now
            filler_status = Status.red.name
            filler_description = Status.red.value
            FILLER_STOP_TIMES += 1

            # Manual Breakdown
            if AUTO_BRAKE_VAR == 0:
                while VAR_STOP_F:
                    # Set Filler Status
                    yield env.timeout(0.01)
                    filler_status = Status.red.name
                    filler_description = Status.red.value

                VAR_STOP_F = True

            # Automated Breakdown
            else:
                # Brake Duration. (Repair After 5-30 min)
                repair_at_filler = start_filler_break + random.uniform(300, 1800)

                while env.now <= repair_at_filler:
                    yield env.timeout(0.01)
                    filler_status = Status.red.name
                    filler_description = Status.red.value
                    # yield env.timeout(random.uniform(300, 1800))

                FILLER_IS_BROKEN = False

            # displayStop("Το Depall έχει τεθεί εκτός λειτουργίας (Status = RED).\n Αιτία: Φρακαρισμένη έξοδος.", env.now)
            finish_filler_break = env.now
            FILLER_STOP_DURATION[FILLER_STOP_TIMES] = finish_filler_break - start_filler_break


threads = list()


def pasteur():
    """Διεργασία του μηχανήματος Pasteur"""
    global pasteur_status, pasteur_description, current_pasteur_level
    global VAR_STOP_P, PASTEUR_RUN_TIMES, PASTEUR_RUN_DURATION, PASTEUR_STOP_TIMES, PASTEUR_STOP_DURATION, PASTEUR_IS_BROKEN
    yield env.timeout(depall_ptime + filler_ptime + 4)

    while True:
        try:
            if not PASTEUR_IS_BROKEN:
                # Επεξεργάζεται όσα κουτιά και αν συναντήσει κάθε pasteur_batch_serve_time
                yield env.timeout(pasteur_batch_serve_time)  # Η μεταφορική τα εισάγει κάθε 30 min

                # Τα βάζει ακαριαία η μεταφορική FP
                print('%.2f: ' % env.now + Fore.LIGHTCYAN_EX + "Filled Cans Before proc: %d " % can_pack_line.filledCans.level + Fore.RESET)
                print('%.2f: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur: ζητά {0} κουτιά απο το Filler για να τα επεξεργαστεί τη στιγμή {1}".format(can_pack_line.filledCans.level, round(env.now, 2)) + Fore.RESET)
                print('%.2f: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur Cans Before proc: %d " % can_pack_line.pastCans.level + Fore.RESET)

                # Set Pasteur Status
                pasteur_description = Status.green.value

                # Πόσα κουτιά έχει σε κάθε batch - όσα βρίσκει παίρνει
                # if cans > batch input = batch else input = level
                if can_pack_line.filledCans.level >= pasteur_batch:
                    pasteur_input = pasteur_batch
                elif can_pack_line.filledCans.level > 0:
                    pasteur_input = can_pack_line.filledCans.level
                else:
                    pasteur_input = 0
                    pass

                print('%.2f: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur Input: %d " % pasteur_input + Fore.RESET)
                current_pasteur_level = pasteur_input

                # Pasteur Process
                def pasteur_process():
                    global current_pasteur_level, pasteur_status, pasteur_description
                    pasteur_run_start = env.now
                    if can_pack_line.filledCans.level != 0:
                        can_pack_line.filledCans.get(pasteur_input)
                        pasteur_status = Status.green.name
                        pasteur_description = Status.green.value
                        print("\nThread is starting\n")
                        env.timeout(pasteur_ptime)
                        pasteur_output = pasteur_input
                        can_pack_line.pastCans.put(pasteur_output)
                        print('%.2f: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur Cans After proc: %d " % can_pack_line.pastCans.level + Fore.RESET)
                        print('%.2f: ' % env.now + Fore.LIGHTCYAN_EX + "Filled Cans After Proc: %d " % can_pack_line.filledCans.level + Fore.RESET)

                    pasteur_run_finish = env.now
                    PASTEUR_RUN_DURATION[PASTEUR_RUN_TIMES] = pasteur_run_finish - pasteur_run_start

                t = threading.Thread(target=pasteur_process, name='t')
                t.start()
                t.join()
                threads.append(t)

        except simpy.Interrupt:
            yield env.timeout(0)
            print("Pasteur has stopped")
            start_pasteur_break = env.now
            pasteur_status = Status.red.name
            pasteur_description = Status.red.value
            PASTEUR_STOP_TIMES += 1

            while VAR_STOP_P:
                # Set Pasteur Status
                yield env.timeout(0.01)
                pasteur_status = Status.red.name
                pasteur_description = Status.red.value

            # Manual Breakdown
            if AUTO_BRAKE_VAR == 0:
                while VAR_STOP_P:
                    # Set Pasteur Status
                    yield env.timeout(0.01)
                    pasteur_status = Status.red.name
                    pasteur_description = Status.red.value

                VAR_STOP_P = True

            # Automated Breakdown
            else:
                # Brake Duration. (Repair After 5-30 min)
                repair_at_pasteur = start_pasteur_break + random.uniform(300, 1800)

                while env.now <= repair_at_pasteur:
                    yield env.timeout(0.01)
                    pasteur_status = Status.red.name

                PASTEUR_IS_BROKEN = False

            finish_pasteur_break = env.now
            PASTEUR_STOP_DURATION[PASTEUR_STOP_TIMES] = finish_pasteur_break - start_pasteur_break


def status_monitoring():
    """Παρακολούθηση μηχανών παραγωγής"""
    global df, depall_status, filler_status, pasteur_status
    global depall_description, filler_description, pasteur_description

    while True:
        yield env.timeout(DT)  # Κάθε χρόνο dt, εισάγει μια εγγραφή
        df = df.append({'ENV_NOW': env.now, 'Depall': depall_description, 'Filler': filler_description, 'Pasteur': pasteur_description}, ignore_index=True)

        write_row({'Env_now': env.now, 'Machine': 'Depall', 'Description': depall_description, 'Current_cans': can_pack_line.depallCans.level, 'Status': depall_status})
        write_row({'Env_now': env.now, 'Machine': 'Filler', 'Description': filler_description, 'Current_cans': can_pack_line.filledCans.level, 'Status': filler_status})
        write_row({'Env_now': env.now, 'Machine': 'Pasteur', 'Description': pasteur_description, 'Current_cans': can_pack_line.pastCans.level, 'Status': pasteur_status})


def live_monitoring():
    """Live Simulation Monitoring"""
    global current_depall_level, current_filler_level, current_pasteur_level
    global VAR_STOP_D, VAR_STOP_F, VAR_STOP_P

    window = Tk()
    window_colour = '#D6EBFE'
    window.title("Live Process Monitoring!")
    window.configure(bg=window_colour)
    window.geometry('1900x1200')

    # Titles
    Label(window, bg="light blue",  relief=GROOVE, text="LIVE PROCESS SIMULATION", font="Arial 25 bold").grid(row=0, sticky='EW', pady=5, columnspan=10)
    # KPIs Title
    Label(window, bg="#C1FBF1", relief=GROOVE, text="KPIs", font="Arial 25 bold").grid(row=9, sticky='EW', pady=10, columnspan=10)
    # Run Title
    Label(window, bg='#878787', relief=GROOVE, text='RUN:', font="Arial 15 bold", fg='#95F920').grid(row=12, column=0, pady=5, ipadx=35)
    # Stand By Title
    Label(window, bg='#878787', relief=GROOVE, text='STAND BY:', font="Arial 15 bold", fg='#E3E132').grid(row=13, column=0, pady=5, ipadx=7)
    # Stop Title
    Label(window, bg='#878787', relief=GROOVE, text='STOP:', font="Arial 15 bold", fg='#BE0000').grid(row=14, column=0, pady=5, ipadx=30)

    # Current Process Time
    pt = Label(window, bg='#6B8CD3', bd=4, height=2, justify=CENTER, relief=GROOVE, text='Elapsed Time: ' + str(round(env.now, 2)) + '  seconds', font="Arial 13 bold ")
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
        Label(window, text=machine_description, font="Arial 14", bg=window_colour, wraplength=140).grid(row=6, column=col, pady=0, sticky=S)
        Label(window, text=str(current_level) + ' / ' + str(machine_capacity), relief=RIDGE, font="Arial 15 bold", justify=CENTER).grid(row=7, column=col, ipadx=i_padx, ipady=15)

    def current_machine_buffer(col, i_padx, current_level, machine_capacity, machine_description):
        """ Current machine level capacity"""
        Label(window, text=machine_description, font="Arial 14", bg=window_colour).grid(row=6, column=col, pady=0, sticky=S)
        Label(window, text=str(current_level) + ' / ' + str(machine_capacity), relief=RIDGE, font="Arial 15 bold", justify=CENTER).grid(row=7, column=col, pady=0, ipadx=i_padx, ipady=15)

    def var_change(machine):
        global VAR_STOP_D, VAR_STOP_F, VAR_STOP_P
        if machine == 'DEPALL':
            VAR_STOP_D = False
        elif machine == 'FILLER':
            VAR_STOP_F = False
        elif machine == 'PASTEUR':
            VAR_STOP_P = False
        print("var change function")

    def manual_brake(col, machine):
        """ Machine Brake Button """
        if AUTO_BRAKE_VAR == 0:
            # Brake Button
            Button(window, text='BRAKE', command=partial(manual_break_and_repair_machine, machine), bg='#D97854', bd=4, font="Arial 13 bold", relief=RAISED, activebackground='#D97854').grid(row=5, column=col, sticky=W, pady=5, padx=100)
            # Repair Button
            RB = Button(window, text='REPAIR', command=partial(var_change, machine), bg='#86D954', bd=4, font="Arial 13 bold", relief=RAISED, activebackground='#86D954')
            RB.grid(row=5, column=col, sticky=E, pady=5, padx=100)
            # return var

    def kpis(col, run_times, run_duration, run_percentage, standby_times, standby_duration, standby_percentage, stop_times, stop_duration, stop_percentage):
        run_percentage += 1
        standby_percentage += 1
        stop_percentage += 1
        # Label (TIMES, DURATION, PERCENTAGE)
        Label(window, bg=window_colour, text='TIMES', font="Arial 15 bold").grid(row=10, column=col, sticky=W, padx=50)
        Label(window, bg=window_colour, text='DURATION', font="Arial 15 bold").grid(row=10, column=col, sticky=E, padx=80)
        # Label(window, bg=window_colour, text='PERCENTAGE', font="Arial 15 bold").grid(row=10, column=col+1, sticky=W, padx=0)

        # Run
        Label(window, bg='#9FE849', padx=30, relief=RIDGE, text=run_times, font="Arial 15 bold").grid(row=12, column=col, sticky=W, padx=40)
        Label(window, bg='#9FE849', padx=30, relief=RIDGE, text=run_duration, font="Arial 15 bold").grid(row=12, column=col, sticky=E, padx=30)
        # Label(window, bg=window_colour, text=str(round(run_percentage, 2)) + ' %', font="Arial 15 bold").grid(row=12, column=col + 1, sticky=W)
        # Stand By
        Label(window, bg='#F5F372', padx=30, relief=RIDGE, text=standby_times, font="Arial 15 bold").grid(row=13, column=col, sticky=W, padx=40)
        Label(window, bg='#F5F372', padx=30, relief=RIDGE, text=standby_duration, font="Arial 15 bold").grid(row=13, column=col, sticky=E, padx=30)
        # Label(window, bg=window_colour, text=str(round(standby_percentage, 2)) + ' %', font="Arial 15 bold").grid(row=13, column=col + 1, sticky=W)
        # Stop
        Label(window, bg='#F57272', padx=30, relief=RIDGE, text=stop_times, font="Arial 15 bold").grid(row=14, column=col, sticky=W, padx=40)
        Label(window, bg='#F57272', padx=30, relief=RIDGE, text=stop_duration, font="Arial 15 bold").grid(row=14, column=col, sticky=E, padx=30)
        # Label(window, bg=window_colour, text=str(round(stop_percentage, 2)) + ' %', font="Arial 15 bold").grid(row=14, column=col + 1, sticky=W)

    # Depall
    D_BL3, D_BL2, D_BL1 = machine_beacon(1, 'DEPALL')
    manual_brake(1, 'DEPALL')
    # Filler
    F_BL3, F_BL2, F_BL1 = machine_beacon(3, 'FILLER')
    manual_brake(3, 'FILLER')
    # PasteurS
    P_BL3, P_BL2, P_BL1 = machine_beacon(5, 'PASTEUR')
    manual_brake(5, 'PASTEUR')

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

    def sim_time_converter(sim_time):
        days = int(sim_time / 86400)
        hours = int((sim_time - (days * 86400)) // 3600)
        minutes = int(sim_time % 3600 / 60)
        seconds = int((sim_time % 3600) % 60)
        return '{:02d}:{:02d}:{:02d}:{:02d}'.format(days, hours, minutes, seconds)
        # return '{:02d}D {:02d}H {:02d}M {:02d}S'.format(days, hours, minutes, seconds)

    depall_run_percentage = []
    depall_standby_percentage = []
    depall_stop_percentage = []

    # Update
    def update():
        if env.now <= SIM_TIME:
            # KPIS(col, run_times, run_duration, run_percentage, standby_times, standby_duration, standby_percentage, stop_times, stop_duration, stop_percentage):
            # Raw Material - Depall
            current_conveyor_capacity_buffer(0, 25, can_pack_line.emptyCans.level, depall_capacity, "Palet Cans Conveyor")
            # Depall
            depall_run_percentage.append(sum(DEPALL_RUN_DURATION.values())/env.now)
            depall_standby_percentage.append(sum(DEPALL_STANDBY_DURATION.values())/env.now)
            depall_stop_percentage.append(sum(DEPALL_STOP_DURATION.values())/env.now)
            # total = sum(depall_run_percentage) + sum(depall_standby_percentage) + sum(depall_stop_percentage)
            current_machine_buffer(1, 125, current_depall_level, depall_batch, "Depall Capacity ")
            kpis(1, double_time_print(DEPALL_RUN_TIMES+DEPALL_STOP_TIMES), duration_converter(DEPALL_RUN_DURATION), sum(depall_run_percentage), double_time_print(DEPALL_STANDBY_TIMES),
                 duration_converter(DEPALL_STANDBY_DURATION), sum(depall_standby_percentage), double_time_print(DEPALL_STOP_TIMES), duration_converter(DEPALL_STOP_DURATION), sum(depall_stop_percentage))
            # Depall - Filler conveyor
            current_conveyor_capacity_buffer(2, 25, can_pack_line.depallCans.level, filler_capacity, "Empty Cans Conveyor")
            # Filler
            current_machine_buffer(3, 135, current_filler_level, filler_batch, "Filler Capacity")
            kpis(3, double_time_print(FILLER_RUN_TIMES+FILLER_STOP_TIMES), duration_converter(FILLER_RUN_DURATION), 0, double_time_print(FILLER_STANDBY_TIMES),
                 duration_converter(FILLER_STANDBY_DURATION), 0, double_time_print(FILLER_STOP_TIMES), duration_converter(FILLER_STOP_DURATION), 0)
            # Filler - Pasteur conveyor
            current_conveyor_capacity_buffer(4, 25, can_pack_line.filledCans.level, pasteur_capacity, "Filled Cans Conveyor")
            # Pasteur
            current_machine_buffer(5, 115, current_pasteur_level, pasteur_batch, "Pasteur Capacity")
            kpis(5, double_time_print(PASTEUR_RUN_TIMES+PASTEUR_STOP_TIMES), duration_converter(PASTEUR_RUN_DURATION), 0, double_time_print(PASTEUR_STANDBY_TIMES),
                 duration_converter(PASTEUR_STANDBY_DURATION), 0, double_time_print(PASTEUR_STOP_TIMES), duration_converter(PASTEUR_STOP_DURATION), 0)
            # Pasteur - _  conveyor
            current_conveyor_capacity_buffer(6, 25, can_pack_line.pastCans.level, 'Inf', "Pasteurised Conveyor")

            beacon_status(depall_status, D_BL3, D_BL2, D_BL1)
            beacon_status(filler_status, F_BL3, F_BL2, F_BL1)
            beacon_status(pasteur_status, P_BL3, P_BL2, P_BL1)

            pt['text'] = 'Elapsed Time: ' + sim_time_converter(env.now)
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

print("\nTotal Production: " + str(can_pack_line.pastCans.level) + " beer cans in " + str(HOURS) + " Hours")
print("Expected Cans Production: {0} cans in {1} Shifts".format(CANS_PER_HOUR * HOURS, HOURS))
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

print("Pasteur function Calls: ", round(sum(PASTEUR_RUN_DURATION) / SIM_TIME))
print("Threads: ", len(threads))

print(DEPALL_STOP_DURATION)
# -------------------------------------------------
'''
# PLOTS
# Plot Gauss Graph
nums = []
for n in range(1000):
    tmp = random.gauss(mu=MU, sigma=SIGMA)
    nums.append(tmp)
plt.hist(nums, bins=200)
plt.show()

# Plot Uniform Graph
gfg = np.random.uniform(low=MIN_PROB, high=MAX_PROB, size=1000)
plt.hist(gfg, bins=50, density=True)
plt.show()
'''
