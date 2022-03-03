import simpy
import random
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

depall_env_time = []

print('----------------------------------')
print("STARTING SIMULATION")

# displayText('Έχει μειωθεί σημαντικά το απόθεμα πρώτης ύλης στο Depall. \n Χρειάζεται ανατροφοδότηση.')

# Αδειάζει το csv για να γράψει τις νέες τιμές
check_csv()

# -------------------------------------------------

# Parameters


# Ακρίβεια αποτελεσμάτων του csv
dt = 10  # in seconds

# SIMULATION RUN TIME
SHIFT = 1  # Simulation time in shifts
SIM_TIME = SHIFT * 8 * 60 * 60  # Simulation time in seconds (57.600)

times = SIM_TIME / dt  # Num of rows in csv

print("Simulation Time = %d min" % SIM_TIME)

dictOut = breakdownOption(SIM_TIME)

print('----------------------------------')
# ---PRODUCTION---
# speed = 20 cans/sec = 72.000 cans/h = 576.000 cans/shift
cans_to_produce = 60000  # cans want to produce per hour
production_speed = round(cans_to_produce / 3600, 2)  # cans per second
print("Production Speed per second: {0} and pes shift: {1}".format(production_speed, cans_to_produce*8))

# ---RAW MATERIAL---
empty_can_capacity = 10  # Χωρητικότητά αποθήκης

# ---RAW MATERIAL - DEPALL CONVEYOR---
RD_conveyor_time = 0  # Θεωρούμε τον χρόνο αμελητέο

# ---DEPALL---
# standard vars
depall_capacity = 50000  # 5000 = 1 παλέτα. Empty cans που μπορούν να περιμένουν μέχρι να επεξεργαστούν
initial_depallCan = 0  # Number αρχικών empty can που έχει το depall
depall_critical_buffer = 500  # Παίρνει ανα 500 τα κουτιά για επεξεργασία = DEPALL BATCH
depall_batch = 500  # 25 sec * process_speed = 25*20 = 500 cans
# dynamic vars
DEPALL_SPEED = production_speed + 5  # 500c/20s
depall_input = depall_batch  # Πόσο προϊόν εισάγει για να επεξεργαστεί (input cans/sec)
depall_ptime = depall_input / DEPALL_SPEED  # Depall Process Time
depall_output = depall_input  # Πόσο προϊόν εξάγει μετά την επεξεργασία (output cans/sec)
MTBF_depall = 31.03  # standard error se min (MTTF)

# ---DEPALL - FILLER CONVEYOR---
# standard vars
DF_conveyor_capacity = 1000  # χωρητικότητα κουτιών πάνω στη μεταφορική
DF_conveyor_initial = 0  # Number αρχικών empty can που έχει η μεταφορική
DF_conveyor_critical_buffer = 500  # Παίρνει ανα 500 τα κουτιά
DF_conveyor_batch = 1
# dynamic vars
DF_CONVEYOR_SPEED = production_speed + 5  # 25 cans/s
DF_conveyor_input = DF_conveyor_batch  # Πόσα κουτιά παίρνει απο το Depall
DF_conveyor_ptime = 5  # Σε πόσο χρόνο τα μεταφέρει απο Depall to Filler
DF_conveyor_output = 1  # Πόσα κουτιά σερβίρει στο Filler
MRBF_DF_conveyor = 20  # standard error se min (MTTF)

# ---FILLER---
# standard vars
filler_capacity = 100  # Depalletized cans που μπορούν να περιμένουν μέχρι να επεξεργαστούν
initial_filledCan = 0  # Number αρχικών depall can που έχει ο filler
filler_critical_buffer = 1
filler_batch = 1
# dynamic vars
FILLER_SPEED = production_speed  # 20 c/s = 1 c/0.05s
filler_input = filler_batch  # Πόσο προϊόν εισάγει για να επεξεργαστεί (input cans/sec)
filler_ptime = filler_input / FILLER_SPEED  # Filler Process Time = 0.05s
filler_output = filler_input  # Πόσο προϊόν εξάγει μετά την επεξεργασία (output cans/sec)
MTBF_filler = 5.34  # standard error se min (MTTF)

# ---FILLER - PASTEUR CONVEYOR---
FP_conveyor_time = 3  # χρόνος για να φτάσει 1 κουτί απο το filler στο pasteur

# ---PASTEUR---
# standard vars
pasteur_capacity = 20000  # Filled cans που μπορούν να περιμένουν μέχρι να επεξεργαστούν
initial_pastCan = 0  # Number αρχικών Filled can που έχει ο Pasteur
pasteur_critical_buffer = 100  # Ανά 100 μπορούν να επεξεργάζονται
pasteur_batch = 100
# dynamic vars
PASTEUR_SPEED = production_speed + 5  # 25 c/s
pasteur_input = pasteur_batch  # Πόσο προϊόν εισάγει για να επεξεργαστεί (input cans/sec)
pasteur_ptime = pasteur_input / PASTEUR_SPEED  # = 100 / 25 = 5 Pasteur Process Time
pasteur_output = pasteur_input  # Πόσο προϊόν εξάγει μετά την επεξεργασία (output cans/sec)
MTBF_pasteur = 25.22  # standard error se min (MTTF)

# Dispatch
dispatch_capacity = 100000000

# ---GENERAL VARIABLES---

RANDOM_SEED = 42  # Reproduce the results

# Num of Repairers
numOfRepairers = 3  # Πόσοι τεχνικοί - χειριστές υπάρχουν στη βάρδια

# Break Point
MIN_MTBF = 2  # Min time in Red Status
REPAIR_DURATION = 30.0  # Duration to repair a machine in  0 -30 minutes

NUM_MACHINES = 3  # Number of machines in Can Production Line

# -------------------------------------------------
# Dataframe Pandas
data = [[0, 'GREEN', 'GREEN', 'GREEN']]
# Create the pandas DataFrame
df = pd.DataFrame(data, columns=['ENV_NOW', 'Depall', 'Filler', 'Pasteur'])


# -------------------------------------------------


class Status(Enum):
    GREEN = Fore.GREEN + "Status = Green: Produce" + Fore.RESET
    ORANGE = Fore.LIGHTYELLOW_EX + "Status = Orange: Stand By" + Fore.RESET
    RED = Fore.RED + "Status = Red: Stopped" + Fore.RESET


# status = Status.ORANGE
# print(status.name, status.value)

def time_to_failure(MTBF):
    """Επιστρέφει το χρόνο που βρίσκεται σε Status Red ένα μηχάνημα"""
    return np.random.uniform(MIN_MTBF, MTBF)


def repair_time():
    return np.random.uniform(4, REPAIR_DURATION)  # Επισκευή απο 4 εως 30λ


def repair_machine(machine, repairers):
    """Εργασία επισκευής μηχανήματος"""
    print('%d: ' % env.now + "Repair of Machine: " + machine + " Started")
    with repairers.request as request:
        yield request
        rep_time = repair_time()
        yield env.timeout(rep_time)
        yield repairers.put(1)  # Επιστρέφει ο Χειριστής
    print('%d: ' % env.now + "Repair of Machine: " + machine + " Completed After: %f minutes" % rep_time)


def cans_rejection():
    """1 to 1000 probability to reject a product. Cause: fail product"""
    if np.random.uniform(1, 1000) == 5:
        rejected_cans = np.random.uniform(1, 5)  # reject from 1 to 5 cans
        return rejected_cans


class CanPackLine(object):

    def __init__(self):
        self.env = env
        # Ορισμός προϊόντων που βγάζει και παίρνει κάθε μηχάνημα
        self.emptyCan = simpy.Container(env)

        # DEPALL
        self.depallCans = simpy.Container(env, capacity=depall_capacity, init=initial_depallCan)
        self.depallCanControl = env.process(self.depall_can_stock_control())

        # DEPALL - FILLER CONVEYOR
        self.conveyorDFCan = simpy.Container(env, capacity=DF_conveyor_capacity, init=DF_conveyor_initial)
        # self.conveyorDFCanControl = env.process(self.conveyorDF_can_stock_control)

        # FILLER
        self.filledCans = simpy.Container(env, capacity=filler_capacity, init=initial_filledCan)
        self.fillerCanControl = env.process(self.filler_batch_buffer())

        # PASTEUR
        self.pastCans = simpy.Container(env, capacity=pasteur_capacity, init=initial_pastCan)
        self.pasteurCanControl = env.process(self.pasteur_batch_buffer())

        # OUTPUT PRODUCT
        self.dispatch = simpy.Container(env, capacity=dispatch_capacity, init=0)

        self.broken = False
        self.repairers = simpy.Resource(env, capacity=numOfRepairers)

        # PROCESS DECLARE & STARTUP
        self.depall_gen = env.process(depall())
        self.conveyorDF_gen = env.process(DF_conveyor())
        self.filler_gen = env.process(filler())
        self.pasteur_fen = env.process(pasteur())

    def depall_can_stock_control(self):
        """Depall Batch: Δεν πρέπει να πέσει κάτω απο 500 κουτιά για να μη σταματήσει να λειτουργεί"""
        yield env.timeout(0)
        while True:
            if self.emptyCan.level < depall_critical_buffer:  # level < 500
                print('%d: ' % env.now + '\x1b[0;30;44m' + 'Έναρξη εργασίας χειριστή.' + '\x1b[0m')
                print('%d: ' % env.now + 'Pallet Can stock bellow critical level ({0}) at {1}'.format(
                    depall_critical_buffer, env.now))
                print('Ενημέρωση Χειριστή οτι έχει μειωθεί σημαντικά το απόθεμα πρώτης ύλης κουτιών')
                pallCanAdded = displayNotification('Έχει μειωθεί σημαντικά το απόθεμα πρώτης ύλης στο Depall.'
                                                   '\nΧρειάζεται ανατροφοδότηση.')
                print("Ο χειριστής πρόσθεσε %d παλεταρισμένα κουτιά." % pallCanAdded)
                time_start = env.now
                yield env.timeout(20)  # Εργασία χειριστή
                yield self.emptyCan.put(pallCanAdded)  # Pall cans που πρόσθεσε ο χειριστής ως πρώτη ύλη στο depall
                print('New empty cans stock is {0}'.format(self.emptyCan.level))
                print('%d: ' % env.now + '\x1b[0;30;44m' + 'Τέλος εργασίας χειριστή μετά απο {:.2f} min.'.format(
                    env.now - time_start) + '\x1b[0m')
                yield env.timeout(2)
            else:
                yield env.timeout(1)  # Κάθε 1 sec ελέγχει την παραγωγή

    def filler_batch_buffer(self):
        """Filler Batch. Στόχος: να μη σταματήσει ποτέ να λειτουργεί ο filler"""
        yield env.timeout(RD_conveyor_time + depall_ptime + DF_conveyor_ptime + 2)
        while True:
            if self.depallCans.level < filler_critical_buffer:  # level < 1
                # print('%d: ' % env.now + '\x1b[0;30;46m' + 'Έναρξη εργασίας χειριστή.' + '\x1b[0m')
                print('%d: ' % env.now + 'Depall Can stock bellow critical level {0} cans at {1}'.format(
                    self.depallCans.level, env.now))
                print('%d: ' % env.now + '\x1b[0;30;46m' + 'Ενημέρωση Συστήματος.' + '\x1b[0m')
                displayAlert(
                    "O Filler έχει τεθεί σε κατάσταση Stand By (Status = ORANGE).\n Αιτία: Δεν έχει 1 κουτί να εισάγει. ")
                write_row({'Env_now': env.now, 'Machine': 'Filler',
                           'Description': 'Δεν υπάρχουν depallCan κουτιά για να γεμιστούν.',
                           'Current_cans': can_pack_line.depallCans.level, 'Status': 'ORANGE'})

                yield env.timeout(RD_conveyor_time + depall_ptime + DF_conveyor_ptime + 2)  # Περίμενε μέχρι να παράξει

                # print('%d: ' % env.now + '\x1b[0;30;46m' + 'Ο χειριστής Ενημερώθηκε!' + '\x1b[0m')
                yield env.timeout(1)
            else:
                yield env.timeout(1)  # Κάθε 1 sec ελέγχει την παραγωγή

    def pasteur_batch_buffer(self):
        """Pasteur Batch. O Pasteur πρέπει να παίρνει ανα 100 τα κουτιά"""
        yield env.timeout(RD_conveyor_time + depall_ptime + DF_conveyor_ptime + filler_ptime + FP_conveyor_time + 3)
        while True:
            if self.filledCans.level < pasteur_critical_buffer:  # level < 100
                # print('%d: ' % env.now + '\x1b[0;30;46m' + 'Έναρξη εργασίας χειριστή.' + '\x1b[0m')
                print('%d: ' % env.now + 'Filled Cans stock bellow critical level ({0}) (<=100) at {1}'.format(
                    self.depallCans.level, env.now))
                print('%d: ' % env.now + '\x1b[0;30;46m' + 'Ενημέρωση Συστήματος.' + '\x1b[0m')
                displayAlert(
                    "O Pasteur έχει τεθεί σε κατάσταση Stand By (Status = ORANGE).\n Αιτία: Δεν έχει 100 κουτιά να παράξει. ")
                write_row({'Env_now': env.now, 'Machine': 'Depall',
                           'Description': 'Δεν υπάρχουν filledCan κουτιά για να παστεριωθούν.',
                           'Current_cans': can_pack_line.filledCans.level, 'Status': 'ORANGE'})

                # Περίμενε μέχρι να παράξουν όλοι οι προηγούμενοι
                yield env.timeout(
                    RD_conveyor_time + depall_ptime + DF_conveyor_ptime + filler_ptime + FP_conveyor_time + 3)

                yield env.timeout(1)
            else:
                yield env.timeout(1)  # Κάθε 1 sec ελέγχει την παραγωγή

    def break_machine(self):
        """Βλάβη μηχανήματος για τυχαίο χρόνο."""
        while True:
            yield self.env.timeout(time_to_failure(MTBF_depall))
            # if not self.broken:
            # Only break the machine if it is currently working.
            # self.process.interrupt()


def depall():
    """Διεργασία του μηχανήματος Depall"""
    while True:
        yield env.timeout(RD_conveyor_time)
        print(
            '%d: ' % env.now + Fore.BLUE + "Depall: ζητά 500 κουτιά για να επεξεργαστεί τη στιγμή %d" % env.now + Fore.RESET)
        # παίρνει 500 cans απο τα emptyCan για να τα επεξεργαστεί (Process: Depalletization)
        write_row({'Env_now': env.now, 'Machine': 'Depall', 'Description': 'Before Process',
                   'Current_cans': can_pack_line.emptyCan.level,
                   'Init_level': initial_depallCan, 'Capacity': depall_capacity, 'Status': 'GREEN'})
        yield can_pack_line.emptyCan.get(depall_input)
        print('%d: ' % env.now + Fore.BLUE + "Empty Cans After proc: %d" % can_pack_line.emptyCan.level + Fore.RESET)
        print(
            '%d: ' % env.now + Fore.BLUE + 'Depall P Start: Αποπαλετοποιεί 500 κουτιά ξεκινώντας τη στιγμή %d' % env.now + Fore.RESET)

        depall_total_ptime.append(depall_ptime)
        depall_env_time.append(env.now)
        # Επεξεργάζεται τα κουτιά για χρόνο ίσο με depall_ptime
        yield env.timeout(depall_ptime)
        print('%d: ' % env.now + Fore.BLUE + "Depall Process Time: %d" % depall_ptime + Fore.RESET)
        # Βγάζει τα επεξεργασμένα cans και τα αποθηκεύσει στο depallCan
        yield can_pack_line.conveyorDFCan.put(depall_output)
        print('%d: ' % env.now + Fore.BLUE + "Depall P Finish: Αποπαλετοποίησε {0} κουτιά τη στιγμή {1}".format(
            depall_output,
            int(env.now)) + Fore.RESET)
        print('%d: ' % env.now + Fore.BLUE + "Depall Cans At Last: %d" % can_pack_line.depallCans.level + Fore.RESET)


def DF_conveyor():
    """Μεταφορά κουτιών απο Depall σε Filler"""
    yield env.timeout(RD_conveyor_time + depall_ptime + 1)
    while True:
        yield env.timeout(0)  # Τα παίρνει ακαριαία απο το Depall
        print(
            '%d: ' % env.now + Fore.MAGENTA + "Conveyor: ζητά 500 κουτιά απο Depall για να σερβίρει τη στιγμή %d" % env.now + Fore.RESET)
        write_row({'Env_now': env.now, 'Machine': 'ConveyorDF', 'Description': 'Πριν μπουν στη μεταφορική',
                   'Current_cans': can_pack_line.conveyorDFCan.level, 'Status': 'GREEN'})
        yield can_pack_line.emptyCan.get(DF_conveyor_input)
        print(
            '%d: ' % env.now + Fore.MAGENTA + "Empty Cans After Conveyor: %d" % can_pack_line.emptyCan.level + Fore.RESET)
        print(
            '%d: ' % env.now + Fore.MAGENTA + 'Conveyor P Start: Μεταφέρθηκαν 500 κουτιά ξεκινώντας τη στιγμή %d' % env.now + Fore.RESET)

        # Χρόνος μεταφορά κουτιών απο Depall σε Filler
        yield env.timeout(DF_conveyor_ptime)
        print('%d: ' % env.now + Fore.MAGENTA + "DF Conveyor Process Time: %d" % DF_conveyor_ptime + Fore.RESET)
        # Βγάζει τα επεξεργασμένα cans και τα αποθηκεύσει στο depallCan
        yield can_pack_line.depallCans.put(DF_conveyor_output)
        print('%d: ' % env.now + Fore.MAGENTA + "DF Conveyor P Finish: Μεταφέρθηκαν {0} κουτιά τη στιγμή {1}".format(
            DF_conveyor_output,
            int(env.now)) + Fore.RESET)
        print(
            '%d: ' % env.now + Fore.MAGENTA + "DF Conveyor Cans At Last: %d" % can_pack_line.depallCans.level + Fore.RESET)


def filler():
    """Διεργασία του μηχανήματος Filler"""
    yield env.timeout(
        RD_conveyor_time + depall_ptime + DF_conveyor_ptime + 2)  # Ξεκινάει μετά απο Χ δευτερόλεπτα απο την έναρξη της παραγωγής

    while True:
        yield env.timeout(0)  # Τα βάζει ακαριαία η μεταφορική DF
        write_row({'Env_now': env.now, 'Machine': 'Filler', 'Description': 'Before Process',
                   'Current Filled cans': can_pack_line.filledCans.level,
                   'Init_level': initial_filledCan, 'Capacity': filler_capacity, 'Status': 'GREEN'})
        print(
            '%d: ' % env.now + Fore.YELLOW + "Depall Cans at Begin: %d " % can_pack_line.depallCans.level + Fore.RESET)
        print(
            '%d: ' % env.now + Fore.YELLOW + "Filler: παίρνει 1 κουτί απο τη μεταφορική για να το επεξεργαστεί τη στιγμή %d" % env.now + Fore.RESET)
        yield can_pack_line.depallCans.get(filler_input)
        print(
            '%d: ' % env.now + Fore.YELLOW + "Depall Cans After Proc: %d" % can_pack_line.depallCans.level + Fore.RESET)
        print(
            '%d: ' % env.now + Fore.YELLOW + 'Filler P Start: Γεμίζει 1000 κουτιά ξεκινώντας τη στιγμή %d' % env.now + Fore.RESET)

        filler_total_ptime.append(filler_ptime)
        yield env.timeout(filler_ptime)
        print('%d: ' % env.now + Fore.YELLOW + "Filler Process Time: {0}".format(filler_ptime) + Fore.RESET)
        yield can_pack_line.filledCans.put(filler_output)
        print('%d: ' % env.now + Fore.YELLOW + "Filler P Finish: Γέμισε {0} κουτιά τη στιγμή {1}".format(filler_output,
                                                                                                         env.now) + Fore.RESET)
        print('%d: ' % env.now + Fore.YELLOW + "Filled Cans At Last: %d " % can_pack_line.filledCans.level + Fore.RESET)


def pasteur():
    """Διεργασία του μηχανήματος Pasteur"""
    yield env.timeout(RD_conveyor_time + depall_ptime + DF_conveyor_ptime + filler_ptime + FP_conveyor_time + 3)
    while True:
        yield env.timeout(FP_conveyor_time)
        write_row({'Env_now': env.now, 'Machine': 'Pasteur', 'Description': 'Before Process',
                   'Current_cans': can_pack_line.pastCans.level,
                   'Init_level': initial_pastCan, 'Capacity': pasteur_capacity, 'Status': 'GREEN'})
        print(
            '%d: ' % env.now + Fore.LIGHTCYAN_EX + "Filled Cans at Begin: %d " % can_pack_line.filledCans.level + Fore.RESET)
        print('%d: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur: ζητά 100 κουτιά απο το Filler "
                                                     "για να τα επεξεργαστεί τη στιγμή %d" % env.now + Fore.RESET)
        yield can_pack_line.filledCans.get(pasteur_input)
        print(
            '%d: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur Cans After Proc: %d" % can_pack_line.pastCans.level + Fore.RESET)

        pasteur_total_ptime.append(pasteur_ptime)
        yield env.timeout(pasteur_ptime)
        print(
            '%d: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur Process Time: {0}".format(pasteur_ptime) + Fore.RESET)
        # yield can_pack_line.pastCan.put(1000)
        print('%d: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur P Finish: Γέμισε {0} κουτιά τη στιγμή {1}".format(
            pasteur_output,
            env.now) + Fore.RESET)
        yield can_pack_line.pastCans.put(pasteur_output)
        print(
            '%d: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur Cans At Last: %d " % can_pack_line.pastCans.level + Fore.RESET)
        yield can_pack_line.dispatch.put(pasteur_output)
        write_row({'Env_now': env.now, 'Machine': 'Pasteur', 'Description': 'Dispatch',
                   'Current_cans': can_pack_line.dispatch.level})


# -------------------------------------------------
random.seed(RANDOM_SEED)  # Reproducing the results

env = simpy.Environment()
can_pack_line = CanPackLine()

# Simulation
env.run(until=SIM_TIME)

print("Συνολικά έχουν παραχθεί: " + str(can_pack_line.dispatch.level) + " κουτιά μπύρας σε " + str(SHIFT) + " βάρδιες")

print('----------------------------------')
print('SIMULATION COMPLETED')
print('----------------------------------')
# gaussianPlot(PT_MEAN_depall, MTTF_depall)

# -------------------------------------------------
# ΜΕΤΡΙΚΕΣ / KPIs

print('\x1b[1;30;45m' + 'ΜΕΤΡΙΚΕΣ / KPIs' + '\x1b[0m')
print(sum(depall_total_ptime))
processTimeConv("Depall", depall_total_ptime, SHIFT)
processTimeConv("Filler", filler_total_ptime, SHIFT)
processTimeConv("Pasteur", pasteur_total_ptime, SHIFT)
