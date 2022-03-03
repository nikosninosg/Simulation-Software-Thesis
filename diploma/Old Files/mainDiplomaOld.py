import simpy
import random
import statistics
from enum import Enum
from windowTkinter import *
from gaussPlot import gaussianPlot

cans_produced = 0  # Teliko proion

print('----------------------------------')
print("STARTING SIMULATION")
print('----------------------------------')
# displayText('Έχει μειωθεί σημαντικά το απόθεμα πρώτης ύλης στο Depall. \n Χρειαζεται ανατροφοδότητση.')

# -------------------------------------------------

# Parameters

# SIMULATION RUN TIME
WEEKS = 5  # Simulation time in weeks
SIM_TIME = WEEKS * 7 * 24 * 60  # Simulation time in minutes
print(SIM_TIME)
# RAW MATERIAL
initial_pallCan = 10000  # Number arxikwn pallet can pou exei to depall = prwth ulh
pall_capasity = 10000  # Posa palletized cans mporei na exoyme sthn arxh (san prwth ylh)

# DEPALL
initial_depallCan = 0  # arithmos arxikwn pall koutiwn poy exei to depall sthn upodoxh gia na epexergastei
depall_capasity = 1000  # palletized cans pou mporei na dextei to depall kai na epejergastei se 1 periodo

# FILLER
initial_filledCan = 0  # arithmos arxikwn depall  koutiwn poy exei o filler sthn upodoxh gia na epexergastei
filler_capasity = 1000  # cans pou mporei na epexergastei o filler se 1 periodo

# PASTEUR
initial_pastCan = 0  # arithmos arxikwn filled koutiwn poy exei o pasteur sthn upodoxh gia na epexergastei
pasteur_capasity = 1000  # filled cans pou mporei na pasteropoiei o pasteur se 1 periodo

# Employees per activity
# Depall
num_depall = 1  # number of depall machines pou 8a xrhsimopoihsoume
PT_MEAN_depall = 10  # Avg. processing time xronos pou xreiazetai to depall gia na apopaletopoihsei 700 koytia / houre
MTTF_depall = 31.03  # standard error se min (MTTF)

# Filler
num_filler = 1  # number of depall machines pou 8a xrhsimopoihsoume
PT_MEAN_filler = 10  # Avg. processing time xronos pou xreiazetai to depall gia na apopaletopoihsei 700 koytia / houre
MTTF_filler = 5.34  # standard error se min (MTTF)

# Pasteur
num_pasteur = 1  # number of depall machines pou 8a xrhsimopoihsoume
PT_MEAN_pasteur = 10  # Avg. processing time xronos pou xreiazetai to depall gia na apopaletopoihsei 700 koytia / houre
MTTF_pasteur = 25.22  # standard error se min (MTTF)

# Dispatch
dispatch_capasity = 100000

RANDOM_SEED = 42

PT_SIGMA = 2.0  # Sigma of processing time

# BREAK_MEAN = 1 / MTTF  # Param. for expovariate distribution
REPAIR_TIME = 30.0  # Time it takes to repair a machine in minutes
JOB_DURATION = 30.0  # Duration of other jobs in minutes

NUM_MACHINES = 3  # Number of machines in Can Production Line

# Critical Levels - Buffers

depall_critical_buffer = depall_capasity / 3  # krisimo shmeio cans pou prepei na exei to depall gia na mh stamtashei na leitourgei
filler_critical_buffer = filler_capasity / 3
pasteur_critical_buffer = pasteur_capasity / 3


# -------------------------------------------------


class Status(Enum):
    GREEN = "Status = Green: Produce"
    ORANGE = "Status = Orange: Stand By"
    RED = "Status = Red: Stopped"


# status = Status.GREEN
# print(status.name, status.value)


class CanPackLine(object):
    def __init__(self, env):
        # orismos twn proiontwν pou vgazei kai pairnei ka8e mhxanhma
        self.palletCan = simpy.Container(env, capacity=pall_capasity, init=initial_pallCan)
        self.depallCanControl = env.process(self.depall_can_stock_control(env))
        self.depallCan = simpy.Container(env, capacity=depall_capasity, init=initial_depallCan)
        self.filledCan = simpy.Container(env, capacity=filler_capasity, init=initial_filledCan)
        self.pastCan = simpy.Container(env, capacity=pasteur_capasity, init=initial_pastCan)
        # self.dispath = simpy.Container(env, capacity=dispatch_capasity, init=0)

    def depall_can_stock_control(self, env):
        yield env.timeout(0)
        while True:
            if self.palletCan.level <= depall_critical_buffer:
                print('Can stock bellow critical level ({0}) at {1}'.format(self.palletCan.level, env.now % 8))
                print('Ενημέρωση Χειριστή οτι έχει μειωθεί σημαντικά το απόθεμα πρώητς ύλης κουτιών')
                pallCanAdded = displayNotification('Έχει μειωθεί σημαντικά το απόθεμα πρώτης ύλης στο Depall.'
                                           ' Χρειαζεται ανατροφοδότητση.')
                print("Ο χειριστής πρόσθεσε %d παλεταρισμένα κουτιά." % pallCanAdded)
                print('----------------------------------')
                yield env.timeout(16)
                yield self.palletCan.put(pallCanAdded)  # pro8hkh #pallCanAdded palletized can gia na mpoun sto depall.
                print('New palletized cans stock is {0}'.format(self.palletCan.level))
                print('----------------------------------')
                yield env.timeout(8)
            else:
                yield env.timeout(1)


def depall(self, can_pack_line):
    while True:
        # pairnei 700 cans apo to palletCan gia na ta epexergastei (Process: Depalletize)
        msg = yield can_pack_line.emptyCans.get(900)
        print('Received this at %d while %s' % (env.now, msg))
        depall_time = random.gauss(PT_MEAN_depall, MTTF_depall)  #

        # epexergazetai ta cans gia periodo ise me depall_time
        yield env.timeout(depall_time)
        # vgazei ta epexergasmena cans kai ta apouhkeuei sto depallCan
        yield can_pack_line.depallCans.put(900)


def filler(self, can_pack_line):
    while True:
        yield can_pack_line.depallCans.get(900)
        filler_time = random.gauss(PT_MEAN_filler, MTTF_filler)
        yield env.timeout(filler_time)
        yield can_pack_line.filledCans.put(667)


def pasteur(self, can_pack_line):
    while True:
        yield can_pack_line.filledCans.get(667)
        pasteur_time = random.gauss(PT_MEAN_pasteur, MTTF_pasteur)
        yield env.timeout(pasteur_time)
        yield can_pack_line.pastCans.put(667)
        # yield can_pack_line.dispatch.put(700)


# Generators

def depall_process_gen(env, can_pack_line):
    for i in range(num_depall):
        env.process(depall(env, can_pack_line))
        yield env.timeout(0)


def filler_process_gen(env, can_pack_line):
    for i in range(num_filler):
        env.process(filler(env, can_pack_line))
        yield env.timeout(0)


def pasteur_process_gen(env, can_pack_line):
    for i in range(num_pasteur):
        env.process(pasteur(env, can_pack_line))
        yield env.timeout(0)


# -------------------------------------------------
random.seed(RANDOM_SEED)

env = simpy.Environment()
can_pack_line = CanPackLine(env)

depall_gen = env.process(depall_process_gen(env, can_pack_line))
filler_gen = env.process(filler_process_gen(env, can_pack_line))
pasteur_fen = env.process(pasteur_process_gen(env, can_pack_line))

# Simulation
env.run(until=SIM_TIME)
print('Stock pallet Cans wait to depalletize: %d' % initial_pallCan)
print('Depall has %d palletized cans!' % can_pack_line.depallCan.level)
print('Filler has %d filled cans!' % can_pack_line.filledCan.level)
print('Pasteur has %d pasteurised cans!' % can_pack_line.pastCan.level)  # dispatch
print('----------------------------------')
print('SIMULATION COMPLETED')

# Μετρικές / KPIs
print('----------------------------------')
gaussianPlot(PT_MEAN_depall, MTTF_depall)
