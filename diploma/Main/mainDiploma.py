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
DEPALL_BRAKE_PROB, FILLER_BRAKE_PROB, PASTEUR_BRAKE_PROB, AUTO_BRAKE_VAR, HOURS, DT = welcomeScreen()
# AUTO_BRAKE_VAR = 0
# Ακρίβεια αποτελεσμάτων - παρακολούθησης | Ακρίβεια δευτερολέπτου
# DT = 100 # in seconds

# SIMULATION RUN TIME
# HOURS = 10  # Simulation time in shifts
SIM_TIME = HOURS * 60 * 60  # Simulation time in seconds

times = SIM_TIME / DT  # Num of rows in csv

print("Simulation Time = %d seconds" % SIM_TIME)
# ---PRODUCTION---
CANS_PER_HOUR = 60000  # cans want to produce per hour
PRODUCTION_SPEED = round(CANS_PER_HOUR / 3600, 2)  # cans per second
print("Production Speed: {0} cans/second and: {1} cans/shift".format(PRODUCTION_SPEED, CANS_PER_HOUR * 8))

# Expected Produced Cans
EXPECTED_CANS = CANS_PER_HOUR * HOURS
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
depall_status = 'green'
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
filler_status = 'green'
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
pasteur_status = 'green'
pasteur_description = "Έναρξη παραγωγής"

# --- RCA VARIABLES ---
# Depall KPIs
DEPALL_IS_BROKEN = False
# D-Run
DEPALL_RUN_TIMES = 1
DEPALL_RUN_DURATION = []
# D-Stand
DEPALL_STANDBY_TIMES = 0
DEPALL_STANDBY_DURATION = {}
# D-Stop
DEPALL_STOP_FLAG = True
DEPALL_STOP_TIMES = 0
DEPALL_STOP_DURATION = {}


# Filler KPIs
FILLER_IS_BROKEN = False
# F-Run
FILLER_RUN_TIMES = 1
FILLER_RUN_DURATION = []
# F-Stand
FILLER_STANDBY_TIMES = 0
FILLER_STANDBY_DURATION = {}
FILLER_STANDBY_FLAG = False  # Για την προς τα εμπρός εκτέλεση
# F-Stop
FILLER_STOP_FLAG = True
FILLER_STOP_TIMES = 0
FILLER_STOP_DURATION = {}

# Pasteur KPIs
PASTEUR_IS_BROKEN = False
# P-Run
PASTEUR_RUN_TIMES = 1
PASTEUR_RUN_DURATION = []
# P-Stand
PASTEUR_STANDBY_TIMES = 0
PASTEUR_STANDBY_DURATION = {}
PASTEUR_STANDBY_FLAG = False
# P-Stop
PASTEUR_STOP_FLAG = True
PASTEUR_STOP_TIMES = 0
PASTEUR_STOP_DURATION = {}


# ---Machine Breakdown---
# Breakdown Probability
BREAK_START = 0
IN_BREAKDOWN = False
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


# DEPALL_BRAKE_PROB = FILLER_BRAKE_PROB = PASTEUR_BRAKE_PROB = 10


def auto_brake_machine():
    """ Automated Breakdown Function with probability """
    global DEPALL_IS_BROKEN, FILLER_IS_BROKEN, PASTEUR_IS_BROKEN

    if AUTO_BRAKE_VAR == 1:
        print("Auto breakdown mode enabled")
        while True:
            # CHECK PERIOD
            yield env.timeout(100)  # SOS
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

    global BREAK_START, IN_BREAKDOWN

    if AUTO_BRAKE_VAR == 0:
        IN_BREAKDOWN = True
        BREAK_START = env.now
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

        # DEPALL - FILLER CONVEYOR
        self.dfControl = env.process(self.depall_filler_conveyor_control())

        # FILLER
        self.filledCans = simpy.Container(env, capacity=pasteur_capacity, init=initial_filledCans)
        self.fillerCanControl = env.process(self.filler_batch_buffer())

        # FILLER - PASTEUR CONVEYOR
        self.fpControl = env.process(self.filler_pasteur_conveyor_control())

        # PASTEUR
        self.pastCans = simpy.Container(env, init=initial_pastCans)
        self.pasteurCanControl = env.process(self.pasteur_batch_buffer())

        # MAIN PROCESS DECLARE & STARTUP
        self.depall_gen = env.process(depall())
        self.filler_gen = env.process(filler())
        self.pasteur_gen = env.process(pasteur())

        # Status & Variable Function Monitoring
        self.status_monitoring_gen = env.process(status_monitoring())

        # Automated Breakdown
        self.auto_brake_machine_gen = env.process(auto_brake_machine())

    def depall_can_stock_control(self):
        """Depall Batch: Δεν πρέπει να πέσει κάτω απο depall_batch κουτιά για να μη σταματήσει να λειτουργεί"""
        global depall_status, depall_description, DEPALL_STANDBY_TIMES, DEPALL_STANDBY_DURATION

        yield env.timeout(0)

        while True:
            if self.emptyCans.level < depall_critical_buffer:  # level < 5000
                # Set Depall Buffer Status
                # DEPALL_STANDBY_TIMES += 1
                # depall_status = Status.yellow.name
                # depall_description = Status.yellow.value

                print('%.2f: ' % env.now + '\x1b[0;30;44m' + 'Έναρξη Εισαγωγής Παλέτας.' + '\x1b[0m')
                print('%.2f: ' % env.now + 'Empty Cans level = {0}'.format(self.emptyCans.level))
                print('%.2f: ' % env.now + "Προστέθηκαν %d παλεταρισμένα κουτιά." % depall_input)

                yield env.timeout(0)  # Εργασία χειριστή
                # displayAlert("Το Depall έχει τεθεί σε κατάσταση Stand By (Status = ORANGE).\n Αιτία: Έχει πέσει κάτω απο 5.000 κουτιά.", env.now)

                # Pall cans που πρόσθεσε ο χειριστής ως πρώτη ύλη στο depall
                yield can_pack_line.emptyCans.put(depall_input)
                print('%.2f: ' % env.now + 'New empty cans stock is {0}'.format(self.emptyCans.level))
                print('%.2f: ' % env.now + '\x1b[0;30;44m' + 'Τέλος Εισαγωγής παλέτας' + '\x1b[0m')
                # depall_standby_finish = env.now
                # DEPALL_STANDBY_DURATION[DEPALL_STANDBY_TIMES] = depall_standby_finish - depall_standby_start

            else:
                yield env.timeout(2)  # Κάθε 2 sec ελέγχει την πρώτη ύλη

    def depall_filler_conveyor_control(self):
        """ IF D-F Conveyor is filled, StandBy Depall process until Filler = Run"""
        global depall_status, depall_description, DEPALL_RUN_TIMES, DEPALL_STANDBY_TIMES, DEPALL_STANDBY_DURATION
        global filler_status

        depall_standby_start = 0
        df_flag = False

        while True:
            yield env.timeout(1)
            if not df_flag and self.depallCans.level == filler_capacity and filler_status != Status.green.name:
                "Αν η μεταφορική γεμίσει και το επόμενο μηχάνημα είναι standby (απο άλλο μηχάνημα - μεταφορική) ή stop: γίνε standby"
                depall_standby_start = env.now
                # Set Depall Status
                depall_status = Status.yellow.name
                depall_description = Status.yellow.value
                yield env.timeout(0)
                print('%.2f: ' % env.now + 'Η μεταφορική Depall - Filler είναι γεμάτη' + '\x1b[0m')
                df_flag = True

            elif df_flag and depall_status == Status.green.name:
                "Μόλις βγει απο το standby αυξάνεται κατά 1"
                DEPALL_RUN_TIMES += 1
                DEPALL_STANDBY_TIMES += 1
                # DEPALL_STANDBY_DURATION.append(env.now - depall_standby_start)
                DEPALL_STANDBY_DURATION[depall_standby_start] = env.now - depall_standby_start
                df_flag = False

            else:
                yield env.timeout(0)

    def filler_batch_buffer(self):
        """Filler Batch. Στόχος: να μη σταματήσει ποτέ να λειτουργεί ο filler"""
        global filler_status, filler_description, FILLER_STANDBY_TIMES, FILLER_STANDBY_DURATION
        global FILLER_STANDBY_FLAG

        yield env.timeout(depall_ptime + filler_ptime + 4)

        while True:
            if self.depallCans.level < filler_critical_buffer:  # level < 1
                filler_standby_start = env.now

                if FILLER_STANDBY_FLAG:
                    FILLER_STANDBY_TIMES += 1
                    FILLER_STANDBY_FLAG = False

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
                # Stand by απο το Depall
                if depall_status == Status.red.name:
                    # FILLER_STANDBY_DURATION.append(env.now - filler_standby_start)
                    FILLER_STANDBY_DURATION[filler_standby_start] = env.now - filler_standby_start

            else:
                yield env.timeout(depall_ptime)  # Κάθε depall_ptime sec ελέγχει την παραγωγή

    def filler_pasteur_conveyor_control(self):
        """ IF F-P Conveyor is filled, StandBy Depall & Filler processes  until Pasteur = Run"""
        global filler_status, filler_description, FILLER_RUN_TIMES, FILLER_STANDBY_TIMES, FILLER_STANDBY_DURATION
        global pasteur_status

        filler_standby_start = 0
        fp_flag = False

        while True:
            yield env.timeout(1)
            if not fp_flag and self.filledCans.level == pasteur_capacity and pasteur_status != Status.green.name:
                "Αν η μεταφορική γεμίσει και το επόμενο μηχάνημα είναι standby (απο άλλο μηχάνημα - μεταφορική) ή stop: γίνε standby"
                filler_standby_start = env.now
                # Set Filler Status
                filler_status = Status.yellow.name
                filler_description = Status.yellow.value
                yield env.timeout(0)
                print('%.2f: ' % env.now + 'Η μεταφορική Filler - Pasteur είναι γεμάτη' + '\x1b[0m')
                fp_flag = True

            elif fp_flag and filler_status == Status.green.name:
                "Μόλις βγει απο το standby αυξάνεται κατά 1"
                FILLER_RUN_TIMES += 1
                FILLER_STANDBY_TIMES += 1
                # Stand by from Pasteur
                # FILLER_STANDBY_DURATION.append(env.now - filler_standby_start)
                FILLER_STANDBY_DURATION[filler_standby_start] = env.now - filler_standby_start
                fp_flag = False

            else:
                yield env.timeout(0)

    def pasteur_batch_buffer(self):
        """Pasteur Batch. O Pasteur πρέπει να παίρνει ανα 1..600 τα κουτιά"""
        global pasteur_status, pasteur_description, PASTEUR_STANDBY_TIMES, PASTEUR_STANDBY_DURATION
        global PASTEUR_STANDBY_FLAG

        yield env.timeout(depall_ptime + filler_ptime + 9)

        while True:
            # Pasteurize 1 to 600 cans
            if self.filledCans.level < pasteur_min_input:
                pasteur_standby_start = env.now

                if PASTEUR_STANDBY_FLAG:
                    PASTEUR_STANDBY_TIMES += 1
                    PASTEUR_STANDBY_FLAG = False

                # Set Status
                pasteur_status = Status.yellow.name
                pasteur_description = Status.yellow.value

                print('%.2f: ' % env.now + '\x1b[0;30;46m' + 'Pasteur: Ενημέρωση Συστήματος.' + '\x1b[0m')
                print('%.2f: ' % env.now + 'Filled Cans stock = {0} bellow critical level < {1} at {2}'.format(self.filledCans.level, pasteur_critical_buffer, env.now))

                # Περίμενε μέχρι να παράξουν όλοι οι προηγούμενοι
                # yield env.timeout(depall_ptime + filler_ptime + 9)

                yield env.timeout(1)
                if depall_status == Status.red.name or filler_status == Status.red.name:
                    # PASTEUR_STANDBY_DURATION.append(env.now - pasteur_standby_start)
                    PASTEUR_STANDBY_DURATION[pasteur_standby_start] = env.now - pasteur_standby_start

            else:
                # yield env.timeout(depall_ptime + filler_ptime + 4)  # Κάθε x sec ελέγχει την παραγωγή
                yield env.timeout(6)


def depall():
    """Διεργασία του μηχανήματος Depall"""
    global depall_status, depall_description, current_depall_level
    global DEPALL_RUN_DURATION, DEPALL_STOP_TIMES, DEPALL_STOP_DURATION, DEPALL_STOP_FLAG, DEPALL_IS_BROKEN
    global FILLER_STANDBY_FLAG, PASTEUR_STANDBY_FLAG, IN_BREAKDOWN

    while True:
        try:
            if can_pack_line.emptyCans.level >= depall_batch and not DEPALL_IS_BROKEN:
                depall_run_start = env.now
                yield env.timeout(0)  # Τα βάζει ακαριαία η μεταφορική RD
                depall_status = Status.green.name
                depall_description = Status.green.value

                print('%.2f: ' % env.now + Fore.BLUE + "Depall: ζητά {0} κουτιά για να επεξεργαστεί τη στιγμή {1}".format(depall_batch, env.now) + Fore.RESET)

                # Παίρνει 500 cans απο τα emptyCan για να τα επεξεργαστεί (Process: Depalletization)
                yield can_pack_line.emptyCans.get(depall_input)
                print('%.2f: ' % env.now + Fore.BLUE + "Empty Cans Before proc: %d" % can_pack_line.emptyCans.level + Fore.RESET)
                print('%.2f: ' % env.now + Fore.BLUE + "Depall Cans Before Proc: %d" % can_pack_line.depallCans.level + Fore.RESET)

                # Τα παίρνει ανα παλέτα (5000) και τα βγάζει 1-1
                for i in range(depall_batch):
                    current_depall_level = depall_batch - i
                    # Set Depall Status
                    depall_status = Status.green.name
                    depall_description = Status.green.value

                    # Επεξεργάζεται τα κουτιά για χρόνο ίσο με depall_ptime
                    yield env.timeout(depall_ptime)
                    yield can_pack_line.depallCans.put(depall_output)
                    print('%.2f: ' % env.now + Fore.BLUE + "Depalletized 1 can at {:.2f}".format(env.now) + Fore.RESET)

                # Βγάζει τα επεξεργασμένα cans και τα αποθηκεύσει στο depallCan
                print('%.2f: ' % env.now + Fore.BLUE + "Empty Cans After proc: %d" % can_pack_line.emptyCans.level + Fore.RESET)
                print('%.2f: ' % env.now + Fore.BLUE + "Depall Cans After Proc: %d" % can_pack_line.depallCans.level + Fore.RESET)

                if DEPALL_STOP_FLAG:
                    DEPALL_RUN_DURATION.append(env.now - depall_run_start)

            else:
                yield env.timeout(0)

        except simpy.Interrupt:
            yield env.timeout(0.01)
            print("Depall has stopped")
            start_depall_break = env.now
            depall_status = Status.red.name
            depall_description = Status.red.value
            DEPALL_STOP_TIMES += 1
            FILLER_STANDBY_FLAG = PASTEUR_STANDBY_FLAG = True  # Θα σηκώσει το flag για να μετρήσει τα sb times του filler

            # Manual Breakdown
            if AUTO_BRAKE_VAR == 0:
                while DEPALL_STOP_FLAG:
                    # Set Depall Status
                    yield env.timeout(0.01)
                    depall_status = Status.red.name
                    depall_description = Status.red.value

                DEPALL_STOP_FLAG = True

            # Automated Breakdown
            else:
                # Brake Duration. (Repair After 5-30 min)
                repair_at = start_depall_break + random.uniform(300, 1800)

                while env.now <= repair_at:
                    yield env.timeout(0.01)
                    depall_status = Status.red.name
                    depall_description = Status.red.value
                    # yield env.timeout(random.uniform(300, 1800))

            # displayStop("Το Depall έχει τεθεί εκτός λειτουργίας (Status = RED).\n Αιτία: Φρακαρισμένη έξοδος.", env.now)
            # DEPALL_STOP_DURATION[DEPALL_STOP_TIMES] = finish_depall_break - start_depall_break
            DEPALL_STOP_DURATION[start_depall_break] = env.now - start_depall_break
            DEPALL_IS_BROKEN = False
            IN_BREAKDOWN = False


def filler():
    """Διεργασία του μηχανήματος Filler"""
    global filler_status, filler_description, current_filler_level
    global FILLER_STOP_FLAG, FILLER_RUN_DURATION, FILLER_STOP_TIMES, FILLER_STOP_DURATION, FILLER_IS_BROKEN, PASTEUR_STANDBY_FLAG
    global IN_BREAKDOWN

    yield env.timeout(depall_ptime + 2)  # Ξεκινάει μετά απο Χ δευτερόλεπτα απο την έναρξη της παραγωγής

    while True:
        try:
            if not FILLER_IS_BROKEN:
                yield env.timeout(0)  # Τα βάζει ακαριαία η μεταφορική DF
                filler_run_start = env.now

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

                FILLER_RUN_DURATION.append(env.now - filler_run_start)

        except simpy.Interrupt:
            yield env.timeout(0)
            print("Filler has stopped")
            start_filler_break = env.now
            filler_status = Status.red.name
            filler_description = Status.red.value
            FILLER_STOP_TIMES += 1
            PASTEUR_STANDBY_FLAG = True

            # Manual Breakdown
            if AUTO_BRAKE_VAR == 0:
                while FILLER_STOP_FLAG:
                    # Set Filler Status
                    yield env.timeout(0.01)
                    filler_status = Status.red.name
                    filler_description = Status.red.value

                FILLER_STOP_FLAG = True

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
            # FILLER_STOP_DURATION[FILLER_STOP_TIMES] = finish_filler_break - start_filler_break
            FILLER_STOP_DURATION[start_filler_break] = env.now - start_filler_break
            IN_BREAKDOWN = False


threads = list()


def pasteur():
    """Διεργασία του μηχανήματος Pasteur"""
    global pasteur_status, pasteur_description, current_pasteur_level
    global PASTEUR_STOP_FLAG, PASTEUR_RUN_DURATION, PASTEUR_STOP_TIMES, PASTEUR_STOP_DURATION, PASTEUR_IS_BROKEN
    global IN_BREAKDOWN

    yield env.timeout(depall_ptime + filler_ptime + 4)

    while True:
        try:
            if not PASTEUR_IS_BROKEN:
                pasteur_run_start = env.now
                # Επεξεργάζεται όσα κουτιά και αν συναντήσει κάθε pasteur_batch_serve_time
                yield env.timeout(pasteur_batch_serve_time)  # Η μεταφορική τα εισάγει κάθε 30 sec

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

                PASTEUR_RUN_DURATION.append(env.now - pasteur_run_start)
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

            while PASTEUR_STOP_FLAG:
                # Set Pasteur Status
                yield env.timeout(0.01)
                pasteur_status = Status.red.name
                pasteur_description = Status.red.value

            # Manual Breakdown
            if AUTO_BRAKE_VAR == 0:
                while PASTEUR_STOP_FLAG:
                    # Set Pasteur Status
                    yield env.timeout(0.01)
                    pasteur_status = Status.red.name
                    pasteur_description = Status.red.value

                PASTEUR_STOP_FLAG = True

            # Automated Breakdown
            else:
                # Brake Duration. (Repair After 5-30 min)
                repair_at_pasteur = start_pasteur_break + random.uniform(300, 1800)

                while env.now <= repair_at_pasteur:
                    yield env.timeout(0.01)
                    pasteur_status = Status.red.name

                PASTEUR_IS_BROKEN = False

            # PASTEUR_STOP_DURATION[PASTEUR_STOP_TIMES] = finish_pasteur_break - start_pasteur_break
            PASTEUR_STOP_DURATION[start_pasteur_break] = env.now - start_pasteur_break
            IN_BREAKDOWN = False


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
    global DEPALL_STOP_FLAG, FILLER_STOP_FLAG, PASTEUR_STOP_FLAG
    global BREAK_START

    window = Tk()
    # window_colour = '#D6EBFE'
    window_colour = '#D6EBFE'
    window.title("Live Process Monitoring!")
    window.configure(bg=window_colour)
    window.geometry('1900x1050')

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

    # Breakdown Duration Calculator
    DUR_WIN = Label(window, bg=window_colour, relief=GROOVE, text='Break duration: ' + str(duration_converter_to_DHMS(0)), font="Arial 15 bold", fg='#BE0000')
    DUR_WIN.grid(row=8, columnspan=20, sticky=W, padx=340)

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
        # Machine Name
        Button(window, bg='#8DCDBA', bd=4, relief=RAISED, text=machine_name, font="Arial 13 bold").grid(row=3, column=col, padx=20, sticky=W)

        return LB3, LB2, LB1

    def current_conveyor_capacity_buffer(col, i_padx, bg_colour, current_level, machine_capacity, machine_description):
        """ Current level capacity status of conveyors """
        Label(window, text=machine_description, font="Arial 14", bg=window_colour, wraplength=140).grid(row=6, column=col, pady=0, sticky=S)
        Label(window, text=str(current_level) + ' / ' + str(machine_capacity), bg=bg_colour, relief=RIDGE, font="Arial 15 bold", justify=CENTER).grid(row=7, column=col, ipadx=i_padx, ipady=15)

    def current_machine_buffer(col, i_padx, bg_colour, current_level, machine_capacity, machine_description):
        """ Current machine level capacity"""
        Label(window, text=machine_description, font="Arial 14", bg=window_colour).grid(row=6, column=col, pady=0, sticky=S)
        Label(window, text=str(current_level) + ' / ' + str(machine_capacity), bg=bg_colour, relief=RIDGE, font="Arial 15 bold", justify=CENTER).grid(row=7, column=col, pady=0, ipadx=i_padx, ipady=15)

    def manual_repair_fun(machine):
        """ Flag for break machines """
        global DEPALL_STOP_FLAG, FILLER_STOP_FLAG, PASTEUR_STOP_FLAG
        if machine == 'DEPALL':
            DEPALL_STOP_FLAG = False
        elif machine == 'FILLER':
            FILLER_STOP_FLAG = False
        elif machine == 'PASTEUR':
            PASTEUR_STOP_FLAG = False
        print("Repair function")

    def manual_brake_button(col, machine):
        """ Machine Brake Button """
        if AUTO_BRAKE_VAR == 0:
            # Break Button
            Button(window, text='BREAK', command=partial(manual_break_and_repair_machine, machine), bg='#D97854', bd=4, font="Arial 13 bold", relief=RAISED, activebackground='#D97854').grid(row=5, column=col, sticky=W, pady=5, padx=100)
            # Repair Button
            RB = Button(window, text='REPAIR', command=partial(manual_repair_fun, machine), bg='#86D954', bd=4, font="Arial 13 bold", relief=RAISED, activebackground='#86D954')
            RB.grid(row=5, column=col, sticky=E, pady=5, padx=100)
            # return var

    def kpis(col, run_times, run_duration, run_percentage, standby_times, standby_duration, standby_percentage, stop_times, stop_duration, stop_percentage):
        """ KPIs Times, Duration about machines """
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
    manual_brake_button(1, 'DEPALL')
    # Filler
    F_BL3, F_BL2, F_BL1 = machine_beacon(3, 'FILLER')
    manual_brake_button(3, 'FILLER')
    # Pasteur
    P_BL3, P_BL2, P_BL1 = machine_beacon(5, 'PASTEUR')
    manual_brake_button(5, 'PASTEUR')

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

    def colour_palette_calc(current_level, capacity):
        x = round((current_level*100)/capacity, 2)
        colour_palette = {0: '#c2f0f0', 1: '#99e6e6', 2: '#70dbdb', 3: '#47d1d1', 4: '#2eb8b8'}
        if 0 <= x < 20:
            return colour_palette[0]
        elif 20 <= x < 40:
            return colour_palette[1]
        elif 40 <= x < 60:
            return colour_palette[2]
        elif 60 <= x < 80:
            return colour_palette[3]
        elif 80 <= x <= 100:
            return colour_palette[4]

    # Update Function for Live Monitoring
    def update():
        """ Update function for UI """

        if env.now <= SIM_TIME:

            DUR_WIN['text'] = 'Break duration: ' + str(duration_converter_to_DHMS(0))
            if AUTO_BRAKE_VAR == 0 and IN_BREAKDOWN:
                # Break Duration Calculator
                DUR_WIN['text'] = 'Break duration: ' + str(duration_converter_to_DHMS(env.now - BREAK_START))

            # KPIS(col, run_times, run_duration, run_percentage, standby_times, standby_duration, standby_percentage, stop_times, stop_duration, stop_percentage):

            # Raw Material - Depall
            current_conveyor_capacity_buffer(0, 25, colour_palette_calc(can_pack_line.emptyCans.level, depall_capacity), can_pack_line.emptyCans.level, depall_capacity, "Palet Cans Conveyor")

            # Depall

            current_machine_buffer(1, 125, colour_palette_calc(current_depall_level, depall_batch), current_depall_level, depall_batch, "Depall Capacity ")
            kpis(1, double_time_print(DEPALL_STANDBY_TIMES+DEPALL_STOP_TIMES), duration_converter_to_DHMS(DEPALL_RUN_DURATION), 0, double_time_print(DEPALL_STANDBY_TIMES),
                 duration_converter_to_DHMS(DEPALL_STANDBY_DURATION), 0, double_time_print(DEPALL_STOP_TIMES), duration_converter_to_DHMS(DEPALL_STOP_DURATION), 0)

            # Depall - Filler conveyor
            current_conveyor_capacity_buffer(2, 25, colour_palette_calc(can_pack_line.depallCans.level, filler_capacity), can_pack_line.depallCans.level, filler_capacity, "Depall Cans Conveyor")

            # Filler
            current_machine_buffer(3, 135, colour_palette_calc(current_filler_level, filler_batch), current_filler_level, filler_batch, "Filler Capacity")
            kpis(3, double_time_print(FILLER_RUN_TIMES+FILLER_STOP_TIMES), duration_converter_to_DHMS(FILLER_RUN_DURATION), 0, double_time_print(FILLER_STANDBY_TIMES),
                 duration_converter_to_DHMS(FILLER_STANDBY_DURATION), 0, double_time_print(FILLER_STOP_TIMES), duration_converter_to_DHMS(FILLER_STOP_DURATION), 0)

            # Filler - Pasteur conveyor
            current_conveyor_capacity_buffer(4, 25, colour_palette_calc(can_pack_line.filledCans.level, pasteur_capacity), can_pack_line.filledCans.level, pasteur_capacity, "Filled Cans Conveyor")

            # Pasteur
            current_machine_buffer(5, 115, colour_palette_calc(current_pasteur_level, pasteur_batch), current_pasteur_level, pasteur_batch, "Pasteur Capacity")
            kpis(5, double_time_print(PASTEUR_RUN_TIMES+PASTEUR_STOP_TIMES), duration_converter_to_DHMS(PASTEUR_RUN_DURATION), 0, double_time_print(PASTEUR_STANDBY_TIMES),
                 duration_converter_to_DHMS(PASTEUR_STANDBY_DURATION), 0, double_time_print(PASTEUR_STOP_TIMES), duration_converter_to_DHMS(PASTEUR_STOP_DURATION), 0)

            # Pasteur - Next Machine conveyor
            current_conveyor_capacity_buffer(6, 25, colour_palette_calc(can_pack_line.pastCans.level, EXPECTED_CANS), can_pack_line.pastCans.level, EXPECTED_CANS, "Pasteurised Conveyor")

            # Beacon Status
            beacon_status(depall_status, D_BL3, D_BL2, D_BL1)
            beacon_status(filler_status, F_BL3, F_BL2, F_BL1)
            beacon_status(pasteur_status, P_BL3, P_BL2, P_BL1)

            pt['text'] = 'Elapsed Time: ' + sim_time_converter(env.now)
            window.after(DT, update)

    update()

    # Close Button
    Button(window, text="Close", height=2, width=10, font="Arial 12 bold ", justify=CENTER, bd='5', bg='#479997', command=window.destroy).grid(row=15, columnspan=10, pady=40)

    window.resizable(True, True)
    window.mainloop()

# -------------------------------------------------
# Outro windows


def outroScreen(D_PERC_SB_, D_PERC_STOP_, F_PERC_SB_, F_PERC_STOP_, P_PERC_SB_, P_PERC_STOP_):
    """ Παράθυρο γενικού σκοπού για τη συνολική εικόνα της γραμμής """
    root = Tk()
    root.geometry("780x600")

    bg_colour = '#D6EBFE'
    root.configure(bg=bg_colour)
    # Title
    Label(root, anchor=CENTER, text='Δείκτες απόδοσης γραμμής', font="Arial 16 bold", bg='#4d94ff', pady=7).grid(row=0, sticky=EW, columnspan=5)

    # Total Time Simulation
    Label(root, text="Συνολική Διάρκεια Simulation: " + str(duration_converter_to_DHMS(SIM_TIME)), font="Arial 14", bg=bg_colour, pady=10).grid(row=1, sticky=W, columnspan=5, padx=30)
    # Production Speed
    Label(root, text="Ταχύτητα παραγωγής της γραμμής: " + str(PRODUCTION_SPEED) + " cans per second", font="Arial 14", bg=bg_colour, pady=10).grid(row=3, sticky=W, columnspan=5, padx=30)
    # Produced products
    Label(root, text="Προϊόντα που παράχθηκαν: " + str(can_pack_line.pastCans.level), font="Arial 14", bg=bg_colour, pady=10).grid(row=4, sticky=W, columnspan=5, padx=30)
    # Expected Products
    Label(root, text="Προϊόντα που αναμέναμε να παραχθούν: " + str(EXPECTED_CANS), font="Arial 14", bg=bg_colour, pady=10).grid(row=5, sticky=W, columnspan=5, padx=30)
    # Overall Production Efficiency
    Label(root, text="Συνολική απόδοση παραγωγής: " + str(round((can_pack_line.pastCans.level/EXPECTED_CANS)*100, 2))+'%', font="Arial 14", bg=bg_colour, pady=10).grid(row=6, sticky=W, columnspan=5, padx=30)

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
        if machine_name == 'DEPALL':
            Button(root, text=machine_name + ' Analysis', height=0, width=15, font="Arial 12 bold", bd='5', bg='light green',
                   activebackground='cyan', command=lambda: additionalAnalysisScreen(machine_name, D_PERC_SB_, D_PERC_STOP_)).grid(row=row, column=4, padx=0, pady=15, sticky=W)
        elif machine_name == 'FILLER':
            Button(root, text=machine_name + ' Analysis', height=0, width=15, font="Arial 12 bold", bd='5', bg='light green',
                   activebackground='cyan', command=lambda: additionalAnalysisScreen(machine_name, F_PERC_SB_, F_PERC_STOP_)).grid(row=row, column=4, padx=0, pady=15, sticky=W)
        elif machine_name == 'PASTEUR':
            Button(root, text=machine_name + ' Analysis', height=0, width=15, font="Arial 12 bold", bd='5', bg='light green',
                   activebackground='cyan', command=lambda: additionalAnalysisScreen(machine_name, P_PERC_SB_, P_PERC_STOP_)).grid(row=row, column=4, padx=0, pady=15, sticky=W)

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


def additionalAnalysisScreen(machine_name, STANDBY_PERCENT_, STOP_PERCENT_, ):
    """ Παράθυρο μηχανήματος για την ανάλυση 1.Efficiency, 2.RCA, 3.Stoppages """
    root = Tk()
    root.geometry("800x900")

    bg_colour = '#D6EBFE'
    root.configure(bg=bg_colour)

    # 1 - Title
    Label(root, anchor=CENTER, text=machine_name + ' Efficiency Analysis', font="Arial 16 bold", bg='#4d94ff', pady=7).grid(row=0, sticky=EW, columnspan=5)
    # Run Percentage
    Label(root, text="Ποσοστό παραγωγής μηχανήματος: " + str(round(100 - (STANDBY_PERCENT_ + STOP_PERCENT_), 2))+'%', font="Arial 14", bg=bg_colour).grid(row=3, sticky=W, columnspan=5, padx=30, pady=5)
    # Production Time
    Label(root, text="Χρόνος παραγωγής μηχανήματος:  " + duration_converter_to_DHMS(((round(100 - (STANDBY_PERCENT_ + STOP_PERCENT_), 2)) * SIM_TIME) / 100), font="Arial 14", bg=bg_colour, pady=10).grid(row=4, sticky=W, columnspan=5, padx=30, pady=5)
    # MTBS
    Label(root, text="MTBS (συνεχόμενος παραγωγικός χρόνος μέχρι το Stop): ", font="Arial 14", bg=bg_colour).grid(row=6, sticky=W, columnspan=5, padx=30, pady=5)

    # 2 - Title RCA
    Label(root, anchor=CENTER, text='Ανάλυση μη παραγωγικού χρόνου', font="Arial 16 bold", bg='#9DF4EB', pady=7).grid(row=8, sticky=EW, columnspan=5)

    def rca_general_info(row, sb_dur):
        # Μην παραγωγικός χρόνος
        Label(root, text='Συνολικός μη παραγωγικός χρόνος: ', font="Arial 14", bg=bg_colour).grid(columnspan=10, row=row, sticky=W, padx=30, pady=5)
        Label(root, text='Συνολικό πλήθος standbys: ' + str(len(sb_dur)), font="Arial 14", bg=bg_colour).grid(columnspan=10, row=row + 1, sticky=W, padx=30, pady=5)
        Label(root, text='Συνολική διάρκεια σε standbys: ' + str(duration_converter_to_DHMS(sb_dur)), font="Arial 14", bg=bg_colour).grid(columnspan=10, row=row + 2, sticky=W, pady=5, padx=30)

    # RCA Title
    Label(root, anchor=CENTER, text='ROOT CAUSE ANALYSIS (RCA)', font="Arial 16 bold underline", bg=bg_colour, pady=7).grid(row=14, sticky=EW, columnspan=5)

    # Column Title
    Label(root, text='ΜΗΧΑΝΗΜΑ', font="Arial 14 bold underline", bg=bg_colour).grid(column=0, row=16, padx=30)
    Label(root, text='ΠΛΗΘΟΣ', font="Arial 14 bold underline", bg=bg_colour).grid(column=1, row=16, padx=30)
    Label(root, text='ΔΙΑΡΚΕΙΑ', font="Arial 14 bold underline", bg=bg_colour).grid(column=2, row=16, padx=30)
    Label(root, text='ΠΟΣΟΣΤΟ', font="Arial 14 bold underline", bg=bg_colour).grid(column=3, row=16, padx=30)

    # Machine Names & Total
    Label(root, text='Depall', font="Arial 14", bg=bg_colour).grid(column=0, row=17, pady=10)
    Label(root, text='Filler', font="Arial 14", bg=bg_colour).grid(column=0, row=18, pady=10)
    Label(root, text='Pasteur', font="Arial 14", bg=bg_colour).grid(column=0, row=19, pady=10)
    Label(root, text='TOTAL', font="Arial 14 bold", bg=bg_colour).grid(column=0, row=20, pady=10)

    # RCA Table
    def RCA_Table(A, B, D, E1, G, H):
        """ RCA TABLE """

        B = sum_converter(B)
        E1 = sum_converter(E1)
        H = sum_converter(H)
        J = A + D + G
        K = B + E1 + H
        if K==0:
            K = 1
        C = round((B / K)*100, 2)
        F = round((E1 / K) * 100, 2)
        I = round((H / K) * 100, 2)
        L = round(C + F + I, 2)

        # Row 17 Depall
        Label(root, text=str(A), font="Arial 14", bg=bg_colour).grid(column=1, row=17)
        Label(root, text=duration_converter_to_M(B), font="Arial 14", bg=bg_colour).grid(column=2, row=17)
        Label(root, text=str(C) + '%', font="Arial 14", bg=bg_colour).grid(column=3, row=17)
        # Row 18 Filler
        Label(root, text=str(D), font="Arial 14", bg=bg_colour).grid(column=1, row=18)
        Label(root, text=duration_converter_to_M(E1), font="Arial 14", bg=bg_colour).grid(column=2, row=18)
        Label(root, text=str(F) + '%', font="Arial 14", bg=bg_colour).grid(column=3, row=18)
        # Row 19 Pasteur
        Label(root, text=str(G), font="Arial 14", bg=bg_colour).grid(column=1, row=19)
        Label(root, text=duration_converter_to_M(H), font="Arial 14", bg=bg_colour).grid(column=2, row=19)
        Label(root, text=str(I) + '%', font="Arial 14", bg=bg_colour).grid(column=3, row=19)
        # Row 20 Total
        Label(root, text=str(J), font="Arial 14", bg=bg_colour).grid(column=1, row=20)
        Label(root, text=duration_converter_to_M(K), font="Arial 14", bg=bg_colour).grid(column=2, row=20)
        Label(root, text=str(L) + '%', font="Arial 14", bg=bg_colour).grid(column=3, row=20)

    # 3 - Stoppages Logs Title

    # Breakdowns Title
    Label(root, anchor=CENTER, text="Stoppages Logs", font="Arial 16 bold", bg='#9DF4EB').grid(row=24, sticky=EW, pady=10, columnspan=4)

    def stoppages_general_info(row, stops_num, stops_dur):
        stops_dur = sum(stops_dur.values())
        Label(root, text="Συνολικό πλήθος breakdowns: " + str(stops_num), font="Arial 14", bg=bg_colour).grid(columnspan=10, sticky=W, row=row, padx=30, pady=5)
        Label(root, text="Συνολική διάρκεια breakdowns: " + str(duration_converter_to_DHMS(stops_dur)), font="Arial 14", bg=bg_colour).grid(columnspan=10, sticky=W, row=row + 1, padx=30, pady=5)
        if stops_num == 0:
            stops_num = 1
        Label(root, text="Μέση διάρκεια βλάβης: " + str(int((stops_dur/stops_num) // 60)) + ' min', font="Arial 14", bg=bg_colour).grid(columnspan=10, sticky=W, row=row+2, padx=30, pady=5)
        Label(root, text="MTBF (Μέσος όρος διάρκειας για τη παρουσίαση βλάβης): " + str(int(((SIM_TIME - stops_dur)/stops_num) // 60)) + ' min', font="Arial 14", bg=bg_colour).grid(columnspan=10, sticky=W, row=row+3, padx=30, pady=5)

    Label(root, text='MACHINE', font="Arial 14 bold underline", bg=bg_colour).grid(column=0, row=29, padx=30)
    Label(root, text='TIME', font="Arial 14 bold underline", bg=bg_colour).grid(column=1, row=29, padx=30)
    Label(root, text='EVENT', font="Arial 14 bold underline", bg=bg_colour).grid(column=2, row=29, padx=30)
    Label(root, text='DURATION', font="Arial 14 bold underline", bg=bg_colour).grid(column=3, row=29, padx=30)

    def standbys_print(row, machine_name_, dictionary):
        i = 0
        for key, value in dictionary.items():
            if i <= 10:
                Label(root, text=machine_name_, font="Arial 14", bg=bg_colour).grid(column=0, row=row + i, padx=30, pady=5)
                Label(root, text=duration_converter_to_DHMS(key), font="Arial 14", bg=bg_colour).grid(column=1, row=row + i, padx=30, pady=5)
                Label(root, text='Stand By', font="Arial 14", bg=bg_colour).grid(column=2, row=row + i, padx=30)
                Label(root, text=duration_converter_to_DHMS(value), font="Arial 14", bg=bg_colour).grid(column=3, row=row + i, padx=30, pady=5)
                i += 1
            else:
                continue

        return row + i

    def breakdowns_print(row, machine_name_, dictionary):
        i = 0
        for key, value in dictionary.items():
            Label(root, text=machine_name_, font="Arial 14", bg=bg_colour).grid(column=0, row=row + i, padx=30, pady=5)
            Label(root, text=duration_converter_to_DHMS(key), font="Arial 14", bg=bg_colour).grid(column=1, row=row + i, padx=30, pady=5)
            Label(root, text='Stop', font="Arial 14", bg=bg_colour).grid(column=2, row=row + i, padx=30)
            Label(root, text=duration_converter_to_DHMS(value), font="Arial 14", bg=bg_colour).grid(column=3, row=row + i, padx=30, pady=5)
            i += 1

    # OEE + ' ('+str((produced_cans/(CANS_PER_HOUR * SHIFT * 8))*100)+'%)'

    if machine_name == 'DEPALL':
        rca_general_info(9, DEPALL_STANDBY_DURATION)
        RCA_Table(DEPALL_STOP_TIMES, DEPALL_STOP_DURATION, FILLER_STANDBY_TIMES, FILLER_STANDBY_DURATION, PASTEUR_STANDBY_TIMES, PASTEUR_STANDBY_DURATION)
        stoppages_general_info(25, DEPALL_STOP_TIMES, DEPALL_STOP_DURATION)
        sd = standbys_print(32, 'Depall', DEPALL_STANDBY_DURATION)
        breakdowns_print(sd+2, 'Depall', DEPALL_STOP_DURATION)
    elif machine_name == 'FILLER':
        rca_general_info(9, FILLER_STANDBY_DURATION)
        RCA_Table(DEPALL_STANDBY_TIMES, DEPALL_STANDBY_DURATION, FILLER_STOP_TIMES, FILLER_STOP_DURATION, PASTEUR_STANDBY_TIMES, PASTEUR_STANDBY_DURATION)
        stoppages_general_info(25, FILLER_STOP_TIMES, FILLER_STOP_DURATION)
        sf = standbys_print(32, 'Filler', FILLER_STANDBY_DURATION)
        breakdowns_print(sf + 2, 'Filler', FILLER_STOP_DURATION)
    elif machine_name == 'PASTEUR':
        rca_general_info(9, PASTEUR_STANDBY_DURATION)
        RCA_Table(DEPALL_STANDBY_TIMES, DEPALL_STANDBY_DURATION, FILLER_STANDBY_TIMES, FILLER_STANDBY_DURATION, PASTEUR_STOP_TIMES, PASTEUR_STOP_DURATION)
        stoppages_general_info(25, PASTEUR_STOP_TIMES, PASTEUR_STOP_DURATION)
        sp = standbys_print(32, 'Pasteur', PASTEUR_STANDBY_DURATION)
        breakdowns_print(sp + 2, 'Pasteur', PASTEUR_STOP_DURATION)

    root.mainloop()


# -------------------------------------------------
# Program Startup
random.seed(RANDOM_SEED)  # Reproducing the results

# Environment Setup
env = simpy.Environment()
can_pack_line = CanPackLine()

threading.Thread(target=live_monitoring).start()

# Start Simulation for time  = SIM_TIME
env.run(until=SIM_TIME)

# -------------------------------------------------
# Metrics - KPIs Calculations
# Standby Percentage
DEPALL_STANDBY_PERCENT = machine_duration_conv_to_perc(DEPALL_STANDBY_DURATION, SIM_TIME)
FILLER_STANDBY_PERCENT = machine_duration_conv_to_perc(FILLER_STANDBY_DURATION, SIM_TIME)
PASTEUR_STANDBY_PERCENT = machine_duration_conv_to_perc(PASTEUR_STANDBY_DURATION, SIM_TIME)
# Stop Percentage
DEPALL_STOP_PERCENT = machine_duration_conv_to_perc(DEPALL_STOP_DURATION, SIM_TIME)
FILLER_STOP_PERCENT = machine_duration_conv_to_perc(FILLER_STOP_DURATION, SIM_TIME)

PASTEUR_STOP_PERCENT = machine_duration_conv_to_perc(PASTEUR_STOP_DURATION, SIM_TIME)


# -------------------------------------------------
# Conclusion - Outro Functions
# Outro Screen for Production Analysis
threading.Thread(target=outroScreen, args=(DEPALL_STANDBY_PERCENT, DEPALL_STOP_PERCENT, FILLER_STANDBY_PERCENT, FILLER_STOP_PERCENT, PASTEUR_STANDBY_PERCENT, PASTEUR_STOP_PERCENT, )).start()

print("\nTotal Production: " + str(can_pack_line.pastCans.level) + " beer cans in " + str(HOURS) + " Hours")
print("Expected Cans Production: {0} cans in {1} Shifts".format(EXPECTED_CANS, HOURS))
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
