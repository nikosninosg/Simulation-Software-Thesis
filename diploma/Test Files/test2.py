import threading
import time
from random import seed, randint
import simpy

seed(23)




def main():
    def print_cube(num):
        """
        function to print cube of given num
        """
        print("Cube: {}".format(num * num * num))

    def print_square(num):
        """
        function to print square of given num
        """
        time.sleep(2)
        print("Square: {}".format(num * num))

        # creating thread

    for i in range(10):
        t1 = threading.Thread(target=print_square, args=(10,))
        t1.start()

    # wait until thread 1 is completely executed
    # t1.join()
    # wait until thread 2 is completely executed
    # t2.join()

    # both threads completely executed

    print("Done!")



class EV:
    def __init__(self, env):
        self.env = env
        self.drive_proc = env.process(self.drive(env))
        self.bat_ctrl_proc = env.process(self.bat_ctrl(env))
        self.bat_ctrl_reactivate = env.event()

    def drive(self, env):
        while True:
            # Drive for 20-40 min
            yield env.timeout(randint(20, 40))
            # Park for 1–6 hours
            print('Start parking at', env.now)
            self.bat_ctrl_reactivate.succeed()  # "reactivate"
            self.bat_ctrl_reactivate = env.event()
            yield env.timeout(randint(60, 360))
            print('Stop parking at', env.now)

    def bat_ctrl(self, env):
        while True:
            print('Bat. ctrl. passivating at', env.now)
            yield self.bat_ctrl_reactivate  # "passivate"
            print('Bat. ctrl. reactivated at', env.now)
            # Intelligent charging behavior here …
            yield env.timeout(randint(30, 90))


env = simpy.Environment()
ev = EV(env)
env.run(until=150)