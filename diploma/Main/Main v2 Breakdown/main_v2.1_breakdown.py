import simpy
import random
import numpy as np
from enum import Enum
from Converters import *
from colorama import Fore
from WindowTkinter import *
import matplotlib.pyplot as plt

cans_produced = 0  # Συνολικά παραγμένα κουτιά
depall_total_ptime = []
filler_total_ptime = []
pasteur_total_ptime = []

depall_env_time = []

print('----------------------------------')
print("STARTING SIMULATION")


# displayText('Έχει μειωθεί σημαντικά το απόθεμα πρώτης ύλης στο Depall. \n Χρειάζεται ανατροφοδότηση.')

# -------------------------------------------------

# Parameters

# Num of Repairers
numOfRepairers = 3

# SIMULATION RUN TIME
WEEKS = 5  # Simulation time in weeks
SIM_TIME = WEEKS * 7 * 24 * 60  # Simulation time in minutes
print("Simulation Time = %d min" % SIM_TIME)

# Επιλογή break μηχανής
dictOut = brakeOption(SIM_TIME)
print(dictOut)


print('----------------------------------')
# RAW MATERIAL
pall_capacity = 1000000  # Posa palletized cans mporei na xwresei to depall
initial_pallCan = 100000  # Number arxikwn pallet can pou exei to depall = prwth ulh

# DEPALL
depall_capacity = 10000  # palletized cans pou mporei na exei to depall kai na epejergastei
initial_depallCan = 0  # arithmos arxikwn pall koutiwn poy exei to depall sthn upodoxh gia na epexergastei
PT_MEAN_depall = 25  # Avg. processing time pou xreiazetai to depall gia na apopaletopoihsei 1000 koytia
MTTF_depall = 31.03  # standard error se min (MTTF)

# FILLER
filler_capacity = 10000  # cans pou mporei na exei gia na epexergastei o filler
initial_filledCan = 0  # arithmos arxikwn depall  koutiwn poy exei o filler sthn upodoxh gia na epexergastei
PT_MEAN_filler = 25  # Avg. processing time pou xreiazetai o filler gia na apopaletopoihsei 1000 koytia
MTTF_filler = 5.34  # standard error se min (MTTF)

# PASTEUR
pasteur_capacity = 10000  # filled cans pou mporei na exei gia na epexergastei
initial_pastCan = 0  # arithmos arxikwn filled koutiwn poy exei o pasteur sthn upodoxh gia na epexergastei
PT_MEAN_pasteur = 25  # Avg. processing time pou xreiazetai o pasteur gia na apopaletopoihsei 1000 koytia
MTTF_pasteur = 25.22  # standard error se min (MTTF)

# Dispatch
dispatch_capacity = 100000000

RANDOM_SEED = 42

PT_SIGMA = 2.0  # Sigma of processing time

# BREAK_MEAN = 1 / MTTF  # Param. for expovariate distribution
REPAIR_TIME = 30.0  # Time it takes to repair a machine in minutes
REPAIR_DURATION = 30.0  # Duration of other jobs in minutes

NUM_MACHINES = 3  # Number of machines in Can Production Line

# Critical Levels - Buffers
depall_critical_buffer = depall_capacity / 3  # krisimo shmeio cans pou prepei na exei to depall gia na mh stamtashei na leitourgei
filler_critical_buffer = filler_capacity / 5
pasteur_critical_buffer = pasteur_capacity / 5


# -------------------------------------------------


class Status(Enum):
    GREEN = Fore.GREEN + "Status = Green: Produce" + Fore.RESET
    ORANGE = Fore.LIGHTYELLOW_EX + "Status = Orange: Stand By" + Fore.RESET
    RED = Fore.RED + "Status = Red: Stopped" + Fore.RESET


# status = Status.ORANGE
# print(status.name, status.value)

def time_to_failure(MTTF):
    """Επιστρέφει το χρόνο που θέλει για να αποτύχει μια μηχανή"""
    BREAK_MEAN = 1 / MTTF  # Param. for expovariate distribution
    return random.expovariate(BREAK_MEAN)


def repair_time():
    return np.random.uniform(4, REPAIR_TIME)  # Επισκευή απο 4 εως 30λ


def repair_machine(machine, repairers):
    """Εργασία επισκευής μηχανήματος"""
    print('%d: ' % env.now + "Repair of Machine: " + machine + " Started")
    with repairers.request as request:
        yield request
        rep_time = repair_time()
        yield env.timeout(rep_time)
        # yield spares.put(1)
    print('%d: ' % env.now + "Repair of Machine: " + machine + " Completed After: %f minutes" % rep_time)


class CanPackLine(object):

    def __init__(self):
        self.env = env
        # Ορισμός προϊόντων που βγάζει και παίρνει κάθε μηχάνημα
        self.palletCan = simpy.Container(env, capacity=pall_capacity, init=initial_pallCan)
        self.depallCanControl = env.process(self.depall_can_stock_control())
        self.depallCan = simpy.Container(env, capacity=depall_capacity, init=initial_depallCan)
        self.fillerCanControl = env.process(self.depall_can_stock_control())
        self.filledCan = simpy.Container(env, capacity=filler_capacity, init=initial_filledCan)
        # self.fillerCanControl = env.process(self.filler_can_stock_control(env))
        self.pastCan = simpy.Container(env, capacity=pasteur_capacity, init=initial_pastCan)
        self.dispatch = simpy.Container(env, capacity=dispatch_capacity, init=0)

        self.broken = False
        self.repairers = simpy.Resource(env, capacity=numOfRepairers)
        self.break_machine

    def depall_can_stock_control(self):
        yield env.timeout(0)
        while True:
            if self.palletCan.level <= depall_critical_buffer:
                print('%d: ' % env.now + '\x1b[0;30;44m' + 'Έναρξη εργασίας χειριστή.' + '\x1b[0m')
                print('%d: ' % env.now + 'Pallet Can stock bellow critical level ({0}) at {1}'.format(
                    depall_critical_buffer, env.now))
                print('Ενημέρωση Χειριστή οτι έχει μειωθεί σημαντικά το απόθεμα πρώτης ύλης κουτιών')
                pallCanAdded = displayNotification('Έχει μειωθεί σημαντικά το απόθεμα πρώτης ύλης στο Depall.'
                                                   '\nΧρειάζεται ανατροφοδότηση.')
                print("Ο χειριστής πρόσθεσε %d παλεταρισμένα κουτιά." % pallCanAdded)
                time_start = env.now
                yield env.timeout(16)
                yield self.palletCan.put(pallCanAdded)  # pro8hkh #pallCanAdded palletized can gia na mpoun sto depall.
                print('New palletized cans stock is {0}'.format(self.palletCan.level))
                print('%d: ' % env.now + '\x1b[0;30;44m' + 'Τέλος εργασίας χειριστή μετά απο {:.2f} min.'.format(
                    env.now - time_start) + '\x1b[0m')
                yield env.timeout(8)
            else:
                yield env.timeout(1)

    def filler_can_stock_control(self, ):
        yield env.timeout(0)
        while True:
            if self.depallCan.level <= filler_critical_buffer:
                # print('%d: ' % env.now + '\x1b[0;30;44m' + 'Έναρξη εργασίας χειριστή.' + '\x1b[0m')
                print('%d: ' % env.now + 'Depall Can stock bellow critical level ({0}) at {1}'.format(
                    self.depallCan.level, env.now))
                print('%d: ' % env.now + '\x1b[0;30;46m' + 'Ενημέρωση χειριστή.' + '\x1b[0m')
                displayAlert(
                    "O Filler πρόκειται να τεθεί σε κατάσταση Stand By (Status = ORANGE).\n Αιτία: Χαμηλό Stock Depall κουτιών. ")  # Μηχάνημα, αιτία
                print("Ο χειριστής Ενημερώθηκε!")

                yield env.timeout(16)
                # yield self.palletCan.put(pallCanAdded)  # pro8hkh #pallCanAdded palletized can gia na mpoun sto depall.
                # ΚΑΠΟΙΑ ΔΙΕΡΓΑΣΙΑ

                print('%d: ' % env.now + '\x1b[0;30;46m' + 'Ο χειριστής Ενημερώθηκε!' + '\x1b[0m')
                yield env.timeout(8)
            else:
                yield env.timeout(1)

    def break_machine(self):
        """Πρόκληση βλάβης μηχανής μόνο αν δουλεύει."""
        while True:
            yield self.env.timeout(time_to_failure(MTTF_depall))
            if not self.broken:
                # Only break the machine if it is currently working.
                self.process.interrupt()


'''


'''


def depall():
    while True:
        yield env.timeout(1)  # 1 min διαρκεί να μπουν 1000 κουτιά στο depall
        print(
            '%d: ' % env.now + Fore.BLUE + "Depall: ζητά 1000 κουτιά για να επεξεργαστεί τη στιγμή %d" % env.now + Fore.RESET)


        # Status = GREEN
        if "Depall" not in dictT:
            # παίρνει 1000 cans απο το palletCan για να τα επεξεργαστεί (Process: Depalletization)
            yield can_pack_line.palletCan.get(1000)
            print(
                '%d: ' % env.now + Fore.BLUE + "Pallet Cans After proc: %d" % can_pack_line.palletCan.level + Fore.RESET)
            print(
                '%d: ' % env.now + Fore.BLUE + 'Depall P Start: Αποπαλετοποιεί 1000 κουτιά ξεκινώντας τη στιγμή %d' % env.now + Fore.RESET)
            depall_ptime = random.gauss(PT_MEAN_depall, MTTF_depall)
            depall_total_ptime.append(depall_ptime)
            depall_env_time.append(env.now)
            # epexergazetai ta cans gia periodo ise me depall_ptime
            yield env.timeout(abs(depall_ptime))
            print('%d: ' % env.now + Fore.BLUE + "Depall Process Time: %f" % abs(depall_ptime) + Fore.RESET)
            # vgazei ta epexergasmena cans kai ta apouhkeuei sto depallCan
            yield can_pack_line.depallCan.put(1000)
            print(
                '%d: ' % env.now + Fore.BLUE + "Depall P Finish: Αποπαλετοποίησε {0} κουτιά τη στιγμή {1}".format(1000,
                                                                                                                  int(env.now)) + Fore.RESET)
        # Status = RED
        else:
            break_machine()

        print('%d: ' % env.now + Fore.BLUE + "Depall Cans At Last: %d" % can_pack_line.depallCan.level + Fore.RESET)


def filler():
    while True:
        yield env.timeout(17)  # 7 min diarkei na mpoun 1000 koutia sto filler
        print('%d: ' % env.now + Fore.YELLOW + "Depall Cans at Begin: %d " % can_pack_line.depallCan.level + Fore.RESET)
        print(
            '%d: ' % env.now + Fore.YELLOW + "Filler: ζητά 1000 κουτιά απο το Depall για να τα επεξεργαστεί τη στιγμή %d" % env.now + Fore.RESET)
        yield can_pack_line.depallCan.get(1000)
        print(
            '%d: ' % env.now + Fore.YELLOW + "Depall Cans After Proc: %d" % can_pack_line.depallCan.level + Fore.RESET)
        print(
            '%d: ' % env.now + Fore.YELLOW + 'Filler P Start: Γεμίζει 1000 κουτιά ξεκινώντας τη στιγμή %d' % env.now + Fore.RESET)
        filler_ptime = random.gauss(PT_MEAN_filler, MTTF_filler)
        filler_total_ptime.append(filler_ptime)
        yield env.timeout(abs(filler_ptime))
        print('%d: ' % env.now + Fore.YELLOW + "Filler Process Time: {0}".format(abs(filler_ptime)) + Fore.RESET)
        yield can_pack_line.filledCan.put(1000)
        print('%d: ' % env.now + Fore.YELLOW + "Filler P Finish: Γέμισε {0} κουτιά τη στιγμή {1}".format(1000,
                                                                                                         env.now) + Fore.RESET)
        print('%d: ' % env.now + Fore.YELLOW + "Filled Cans At Last: %d " % can_pack_line.filledCan.level + Fore.RESET)


def pasteur():
    while True:
        yield env.timeout(27)
        print(
            '%d: ' % env.now + Fore.LIGHTCYAN_EX + "Filled Cans at Begin: %d " % can_pack_line.filledCan.level + Fore.RESET)
        print('%d: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur: ζητά 1000 κουτιά απο το Filler "
                                                     "για να τα επεξεργαστεί τη στιγμή %d" % env.now + Fore.RESET)
        yield can_pack_line.filledCan.get(1000)
        print(
            '%d: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur Cans After Proc: %d" % can_pack_line.pastCan.level + Fore.RESET)
        pasteur_ptime = random.gauss(PT_MEAN_pasteur, MTTF_pasteur)
        pasteur_total_ptime.append(pasteur_ptime)
        yield env.timeout(abs(pasteur_ptime))
        print(
            '%d: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur Process Time: {0}".format(abs(pasteur_ptime)) + Fore.RESET)
        # yield can_pack_line.pastCan.put(1000)
        print('%d: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur P Finish: Γέμισε {0} κουτιά τη στιγμή {1}".format(1000,
                                                                                                                env.now) + Fore.RESET)
        yield can_pack_line.dispatch.put(1000)
        print(
            '%d: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur Cans At Last: %d " % can_pack_line.pastCan.level + Fore.RESET)


def observe():
    while True:
        pasteur_total_ptime.append(env.now)

        yield env.timeout(1)


# -------------------------------------------------
random.seed(RANDOM_SEED)  # Reproducing the results

env = simpy.Environment()
can_pack_line = CanPackLine()

depall_gen = env.process(depall())
filler_gen = env.process(filler())
pasteur_fen = env.process(pasteur())

# Simulation
env.run(until=SIM_TIME)
print('Depall has %d depalletized cans!' % can_pack_line.depallCan.level)
print('Filler has %d filled cans!' % can_pack_line.filledCan.level)
print('Pasteur has %d pasteurised cans!' % can_pack_line.pastCan.level)  # dispatch

print("Συνολικά έχουν παραχθεί: %d κουτιά μπύρας" % can_pack_line.dispatch.level)

print('----------------------------------')
print('SIMULATION COMPLETED')

# Μετρικές / KPIs
print('----------------------------------')
# gaussianPlot(PT_MEAN_depall, MTTF_depall)

# -------------------------------------------------
# ΜΕΤΡΙΚΕΣ / KPIs

print('\x1b[1;30;45m' + 'ΜΕΤΡΙΚΕΣ / KPIs' + '\x1b[0m')
processTimeConv("Depall", depall_total_ptime, WEEKS)
processTimeConv("Filler", filler_total_ptime, WEEKS)
processTimeConv("Pasteur", pasteur_total_ptime, WEEKS)

plt.figure()
plt.step(depall_env_time, depall_total_ptime, where='post')
plt.xlabel('Time (minutes)')
plt.ylabel('Depall Process Time')
plt.show()










'''

# Process Declare & Start Up
sim_time = 100
while (sim_time):
    self.depall_gen = env.process(depall())
    self.filler_gen = env.process(filler())
    self.pasteur_fen = env.process(pasteur())
    sleep dt


    def machine(machine_timeout):
        while True:
            yield env.timeout(machine_timeout)  # 7 διαρκεί να μπουν τα κουτιά στο filler
            print(
                '%d: ' % env.now + Fore.YELLOW + "Depall Cans at Begin: %d " % can_pack_line.machine_lvl.level + Fore.RESET)
            print(
                '%d: ' % env.now + Fore.YELLOW + "Filler: ζητά 1000 κουτιά απο το Depall για να τα επεξεργαστεί τη στιγμή %d" % env.now + Fore.RESET)
            yield can_pack_line.depallCan.get(1000)
            print(
                '%d: ' % env.now + Fore.YELLOW + "Depall Cans After Proc: %d" % can_pack_line.depallCan.level + Fore.RESET)
            print(
                '%d: ' % env.now + Fore.YELLOW + 'Filler P Start: Γεμίζει 1000 κουτιά ξεκινώντας τη στιγμή %d' % env.now + Fore.RESET)
            filler_ptime = random.gauss(PT_MEAN_filler, MTTF_filler)
            filler_total_ptime.append(filler_ptime)
            yield env.timeout(abs(filler_ptime))
            print('%d: ' % env.now + Fore.YELLOW + "Filler Process Time: {0}".format(abs(filler_ptime)) + Fore.RESET)
            yield can_pack_line.filledCan.put(1000)
            print('%d: ' % env.now + Fore.YELLOW + "Filler P Finish: Γέμισε {0} κουτιά τη στιγμή {1}".format(1000,
                                                                                                             env.now) + Fore.RESET)
            print(
                '%d: ' % env.now + Fore.YELLOW + "Filled Cans At Last: %d " % can_pack_line.filledCan.level + Fore.RESET)
'''