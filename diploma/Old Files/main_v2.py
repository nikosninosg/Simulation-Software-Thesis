import simpy
import random
import numpy as np
from enum import Enum
from colorama import Fore
from WindowTkinter import *
import matplotlib.pyplot as plt


print('----------------------------------')
print("STARTING SIMULATION")

# displayText('Έχει μειωθεί σημαντικά το απόθεμα πρώτης ύλης στο Depall. \n Χρειαζεται ανατροφοδότητση.')

# -------------------------------------------------

# Parameters

# Num of Repairers
numOfRepairers = 3

# SIMULATION RUN TIME
WEEKS = 5  # Simulation time in weeks
SIM_TIME = WEEKS * 7 * 24 * 60  # Simulation time in minutes
print("Simulation Time = %d mins" % SIM_TIME)
print('----------------------------------')
# RAW MATERIAL
initial_pallCan = 10000  # Number arxikwn pallet can pou exei to depall = prwth ulh
pall_capasity = 1000000  # Posa palletized cans mporei na xwresei to depall

# DEPALL
initial_depallCan = 0  # arithmos arxikwn pall koutiwn poy exei to depall sthn upodoxh gia na epexergastei
depall_capasity = 10000  # palletized cans pou mporei na dextei to depall kai na epejergastei se 1 periodo
PT_MEAN_depall = 10  # Avg. processing time xronos pou xreiazetai to depall gia na apopaletopoihsei 700 koytia / houre
MTTF_depall = 31.03  # standard error se min (MTTF)

# FILLER
initial_filledCan = 0  # arithmos arxikwn depall  koutiwn poy exei o filler sthn upodoxh gia na epexergastei
filler_capasity = 1000  # cans pou mporei na epexergastei o filler se 1 periodo

# PASTEUR
initial_pastCan = 0  # arithmos arxikwn filled koutiwn poy exei o pasteur sthn upodoxh gia na epexergastei
pasteur_capasity = 1000  # filled cans pou mporei na pasteropoiei o pasteur se 1 periodo

# Employees per activity
# Depall
num_depall = 1  # number of depall machines pou 8a xrhsimopoihsoume

# Filler
num_filler = 1  # number of depall machines pou 8a xrhsimopoihsoume
PT_MEAN_filler = 10  # Avg. processing time xronos pou xreiazetai to depall gia na apopaletopoihsei 700 koytia / houre
MTTF_filler = 5.34  # standard error se min (MTTF)

# Pasteur
num_pasteur = 1  # number of depall machines pou 8a xrhsimopoihsoume
PT_MEAN_pasteur = 10  # Avg. processing time xronos pou xreiazetai to depall gia na apopaletopoihsei 700 koytia / houre
MTTF_pasteur = 25.22  # standard error se min (MTTF)

# Dispatch
dispatch_capacity = 100000

RANDOM_SEED = 42

PT_SIGMA = 2.0  # Sigma of processing time

# BREAK_MEAN = 1 / MTTF  # Param. for expovariate distribution
REPAIR_TIME = 30.0  # Time it takes to repair a machine in minutes
REPAIR_DURATION = 30.0  # Duration of other jobs in minutes

NUM_MACHINES = 3  # Number of machines in Can Production Line

# Critical Levels - Buffers
depall_critical_buffer = depall_capasity / 3  # krisimo shmeio cans pou prepei na exei to depall gia na mh stamtashei na leitourgei
filler_critical_buffer = filler_capasity / 3
pasteur_critical_buffer = pasteur_capasity / 3


# -------------------------------------------------


class Status(Enum):
    GREEN = Fore.GREEN + "Status = Green: Produce" + Fore.RESET
    ORANGE = Fore.LIGHTYELLOW_EX + "Status = Orange: Stand By" + Fore.RESET
    RED = Fore.RED + "Status = Red: Stopped" + Fore.RESET


# status = Status.ORANGE
# print(status.name, status.value)

def time_to_failure(MTTF):
    """Return time until next failure for a machine."""
    BREAK_MEAN = 1 / MTTF  # Param. for expovariate distribution
    return random.expovariate(BREAK_MEAN)


def repair_time():
    return np.random.uniform(4, REPAIR_TIME)


def repair_machine(env, repairers):
    """Εργασία επισκευής μηχανήματος"""
    with repairers.request as request:
        yield request
        yield env.timeout(repair_time())
        # yield
    print('%d: ' % env.now + "Repair Completed")


class CanPackLine(object):
    def __init__(self, name, repairers):
        # orismos twn proiontwν pou vgazei kai pairnei ka8e mhxanhma
        self.palletCan = simpy.Container(env, capacity=pall_capasity, init=initial_pallCan)
        self.depallCanControl = env.process(self.depall_can_stock_control(env))
        self.depallCan = simpy.Container(env, capacity=depall_capasity, init=initial_depallCan)
        self.filledCan = simpy.Container(env, capacity=filler_capasity, init=initial_filledCan)
        # self.fillerCanControl = env.process(self.filler_can_stock_control(env))
        self.pastCan = simpy.Container(env, capacity=pasteur_capasity, init=initial_pastCan)
        self.dispatch = simpy.Container(env, capacity=dispatch_capacity, init=0)

        self.env = env
        self.cans_produced = 0  # Teliko proion
        self.name = name
        self.broken = False
        self.repairers = simpy.Resource(env, capacity=numOfRepairers)

    def depall_can_stock_control(self, env):
        yield env.timeout(0)
        while True:
            if self.palletCan.level <= depall_critical_buffer:
                print('%d: ' % env.now + '\x1b[0;30;44m' + 'Έναρξη εργασίας χειριστή.' + '\x1b[0m')
                print('%d: ' % env.now + 'Pallet Can stock bellow critical level ({0}) at {1}'.format(
                    self.palletCan.level, env.now))
                print('Ενημέρωση Χειριστή οτι έχει μειωθεί σημαντικά το απόθεμα πρώτης ύλης κουτιών')
                pallCanAdded = displayNotification('Έχει μειωθεί σημαντικά το απόθεμα πρώτης ύλης στο Depall.'
                                                   ' Χρειαζεται ανατροφοδότητση.')
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

    def break_machine(self):
        """Βλάβη σε μηχανή σε τυχαίο χρόνο."""
        while True:
            yield self.env.timeout(time_to_failure(MTTF_depall))
            if not self.broken:
                # Only break the machine if it is currently working.
                self.process.interrupt()


'''
    def filler_can_stock_control(self, env):
        yield env.timeout(40)
        while True:
            if self.depallCan.level <= filler_critical_buffer:
                # print('%d: ' % env.now + '\x1b[0;30;44m' + 'Έναρξη εργασίας χειριστή.' + '\x1b[0m')
                print('%d: ' % env.now + 'Depall Can stock bellow critical level ({0}) at {1}'.format(self.depallCan.level, env.now))
                print('%d: ' % env.now + '\x1b[0;30;46m' + 'Ενημέρωση χειριστή.' + '\x1b[0m')
                displayAlert("Filler", 'Μπλοκαρισμένη είσοδος')  # Μηχάνημα, αιτία
                # print("Ο χειριστής Ενημερώθηκε!")
                yield env.timeout(16)
                # yield self.palletCan.put(pallCanAdded)  # pro8hkh #pallCanAdded palletized can gia na mpoun sto depall.

                # ΚΑΠΟΙΑ ΔΙΕΡΓΑΣΙΑ

                print('%d: ' % env.now + '\x1b[0;30;46m' + 'Ο χειριστής Ενημερώθηκε!' + '\x1b[0m')
                yield env.timeout(8)
            else:
                yield env.timeout(1)

'''


def depall(self, can_pack_line):
    while True:
        yield env.timeout(time_to_failure(MTTF_depall))  # xronos pou paramenei se katastassh broken
        t_broken = env.now
        print('%d: ' % env.now + Fore.BLUE + "Depall: Broke" + Fore.RESET)
        # launch repair process
        #env.process(repair_machine(env, repairers))

        print(
            '%d: ' % env.now + Fore.BLUE + "Depall: ζητά 1000 κουτιά για να επεξεργαστεί τη στιγμή %d" % env.now + Fore.RESET)
        # pairnei 1000 cans apo to palletCan gia na ta epexergastei (Process: Depalletize)
        yield can_pack_line.emptyCans.get(1000)

        t_replaced = env.now
        print('%d: ' % env.now + Fore.BLUE + "Depall: Replaced" + Fore.RESET)
        print('%d: ' % env.now + Fore.BLUE + "Pallet Cans: %d" % can_pack_line.emptyCans.level + Fore.RESET)
        print(
            '%d: ' % env.now + Fore.BLUE + 'Depall P Start: Αποπαλετοποιεί 1000 κουτιά ξεκινώντας τη στιγμή %d' % env.now + Fore.RESET)
        depall_time = random.gauss(PT_MEAN_depall, MTTF_depall)
        # epexergazetai ta cans gia periodo ise me depall_time
        yield env.timeout(abs(depall_time))
        print('%d: ' % env.now + Fore.BLUE + "Depall Process Time: %f" % abs(depall_time) + Fore.RESET)
        # vgazei ta epexergasmena cans kai ta apouhkeuei sto depallCan
        yield can_pack_line.depallCans.put(1000)
        print('%d: ' % env.now + Fore.BLUE + "Depall P Finish: Αποπαλετοποίησε {0} κουτιά τη στιγμή {1}".format(1000,
                                                                                                                env.now) + Fore.RESET)
        print('%d: ' % env.now + Fore.BLUE + "Depall Cans: %d" % can_pack_line.depallCans.level + Fore.RESET)

def filler(self, can_pack_line):
    while True:
        yield env.timeout(37)  # 7 min diarkei na mpoun 1000 koutia sto filler
        print('%d: ' % env.now + Fore.YELLOW + "Depall Cans at Begin: %d " % can_pack_line.depallCans.level + Fore.RESET)
        print(
            '%d: ' % env.now + Fore.YELLOW + "Filler: ζητά 1000 κουτιά απο το Depall για να τα επεξεργαστεί τη στιγμή %d" % env.now + Fore.RESET)
        yield can_pack_line.depallCans.get(1000)
        print(
            '%d: ' % env.now + Fore.YELLOW + "Depall Cans After Proc: %d" % can_pack_line.depallCans.level + Fore.RESET)
        print(
            '%d: ' % env.now + Fore.YELLOW + 'Filler P Start: Γεμίζει 1000 κουτιά ξεκινώντας τη στιγμή %d' % env.now + Fore.RESET)
        filler_time = random.gauss(PT_MEAN_filler, MTTF_filler)
        yield env.timeout(abs(filler_time))
        print('%d: ' % env.now + Fore.YELLOW + "Filler Process Time: {0}".format(abs(filler_time)) + Fore.RESET)
        yield can_pack_line.filledCans.put(1000)
        print('%d: ' % env.now + Fore.YELLOW + "Filler P Finish: Γέμισε {0} κουτιά τη στιγμή {1}".format(1000,
                                                                                                         env.now) + Fore.RESET)
        print('%d: ' % env.now + Fore.YELLOW + "Filled Cans At Last: %d " % can_pack_line.filledCans.level + Fore.RESET)


def pasteur(self, can_pack_line):
    while True:
        yield env.timeout(87)
        print('%d: ' % env.now + Fore.LIGHTCYAN_EX + "Filled Cans at Begin: %d " % can_pack_line.filledCans.level + Fore.RESET)
        print('%d: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur: ζητά 1000 κουτιά απο το Filler "
                                                     "για να τα επεξεργαστεί τη στιγμή %d" % env.now + Fore.RESET)
        yield can_pack_line.filledCans.get(1000)
        print(
            '%d: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur Cans After Proc: %d" % can_pack_line.pastCans.level + Fore.RESET)
        pasteur_time = random.gauss(PT_MEAN_pasteur, MTTF_pasteur)
        yield env.timeout(abs(pasteur_time))
        print('%d: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur Process Time: {0}".format(abs(pasteur_time)) + Fore.RESET)
        # yield can_pack_line.pastCan.put(1000)
        print('%d: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur P Finish: Γέμισε {0} κουτιά τη στιγμή {1}".format(1000,
                                                                                                                env.now) + Fore.RESET)
        yield can_pack_line.dispatch.put(1000)
        print(
            '%d: ' % env.now + Fore.LIGHTCYAN_EX + "Pasteur Cans At Last: %d " % can_pack_line.pastCans.level + Fore.RESET)


# -------------------------------------------------
random.seed(RANDOM_SEED)  # Ξανα παράγει τα αποτελέσματα

env = simpy.Environment()
can_pack_line = CanPackLine(env)

depall_gen = env.process(depall(env, can_pack_line))
filler_gen = env.process(filler(env, can_pack_line))
pasteur_fen = env.process(pasteur(env, can_pack_line))

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

'''
plt.figure()
plt.step( ,  , where='post')
plt.xlabel('')
plt.ylabel('')
'''
