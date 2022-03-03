from OutputCSV import *
from WindowTkinter import *

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
depall_status = 'orange'
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
filler_status = 'orange'
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
pasteur_status = 'orange'
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
