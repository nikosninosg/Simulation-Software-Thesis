from tqdm import tqdm
import time
from alive_progress import alive_bar
from alive_progress import config_handler
import progressbar

'''
config_handler.set_global(length=20, spinner='wait')
with alive_bar(1000, bar='blocks', spinner='twirls') as bar:
    for i in range(1000):
        time.sleep(.005)
        if i and i % 300 == 0:
            print('cool')
        bar()

'''


for i in progressbar.progressbar(range(100), redirect_stdout=True):
    print('Some text', i)
    time.sleep(0.1)

def loadbar(total_time):

    for i in tqdm(range(total_time), desc="Simulation in progress", ncols=100):
        pass
