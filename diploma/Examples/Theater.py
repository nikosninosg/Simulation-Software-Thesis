import simpy
import random
import statistics
import itertools

wait_times = []


class Theater(object):
    def __init__(self, env, num_cashiers, num_servers, num_ushers):
        self.env = env
        self.cashier = simpy.Resource(env, num_cashiers)
        self.server = simpy.Resource(env, num_servers)
        self.usher = simpy.Resource(env, num_ushers)

    def purchase_ticket(self):
        yield self.env.timeout(random.randint(1, 3))

    def check_ticket(self):
        yield self.env.timeout(3 / 60)

    def sell_food(self):
        yield self.env.timeout(random.randint(1, 5))


def go_to_movies(env, moviegoer, theater):
    # Moviegoer arrives at the theater
    arrival_time = env.now

    with theater.cashier.request() as request:
        yield request
        yield env.process(theater.purchase_ticket(moviegoer))

    with theater.usher.request() as request:
        yield request
        yield env.process(theater.check_ticket(moviegoer))

    if random.choice([True, False]):
        with theater.server.request() as request:
            yield request
            yield env.process(theater.sell_food(moviegoer))

    # Moviegoer heads into the theater
    wait_times.append(env.now - arrival_time)


def run_theater(env, num_cashiers, num_servers, num_ushers, moviegoers):
    theater = Theater(env, num_cashiers, num_servers, num_ushers)

    for moviegoer in range(3):
        env.process(go_to_movies(env, moviegoer, theater))

    while moviegoers > moviegoer:
        yield env.timeout(0.20)  # Wait a bit before generating a new person

        moviegoer += 1
        env.process(go_to_movies(env, moviegoer, theater))


def get_user_input():
    moviegoers = input("How many moviegoers do you expect today? ")
    max_cashiers = input("Input maximum # of cashiers working: ")
    max_servers = input("Input maximum # of servers working: ")
    max_ushers = input("Input maximum # of ushers working: ")
    max_time = input("Whats the maximum waiting time: ")
    params = [moviegoers, max_cashiers, max_servers, max_ushers, max_time]
    if all(str(i).isdigit() for i in params):  # Check input is valid
        params = [int(x) for x in params]
    else:
        print(
            "Could not parse input. Simulation will use default values:",
            "\n200 moviegoers 10 max cashier, 10 max server, 10 max usher and max waiting time 10min.",
        )
        params = [200, 10, 10, 10, 10]
    return params


def show_optimum_solution(stats, maxtime):
    # extract all simulation runs where waiting time was below maxtime
    time_under_max = list(filter(lambda x: x[1] <= maxtime, stats))
    # if none where found add 1 to maxtime and try again
    while len(time_under_max) == 0:
        print(
            f"Warning: no employee configuration found with avg waiting time below {maxtime}! Changeing maxtime to {maxtime + 1}")
        maxtime = maxtime + 1
        time_under_max = list(filter(lambda x: x[1] <= maxtime, stats))

    # find the solution with the lowest number of employees
    optimal_low_employ = min(time_under_max, key=lambda x: sum(x[0]))

    opti_cashier = optimal_low_employ[0][0]
    opti_servers = optimal_low_employ[0][1]
    opti_ushers = optimal_low_employ[0][2]
    # extract minutes and seconds
    minutes, frac_minutes = divmod(optimal_low_employ[1], 1)
    seconds = frac_minutes * 60
    print(
        f"Optimized solution for max avg waiting time <= {maxtime} is Cashiers: {opti_cashier} , Servers: {opti_servers} , Ushers: {opti_ushers} with avg waiting time: {round(minutes)} min and {round(seconds)} seconds")


def main():
    # Setup our list to safe parameters and times for all iterations
    stats_per_run = []

    # get user input for simulation setup
    movgoers, max_cashiers, max_servers, max_ushers, max_wait = get_user_input()

    # setting up the nested list so itertools.product can generate all combinations for num_cashiers, num_servers and num_ushers parameters
    combs = [list(range(1, max_cashiers + 1)), list(range(1, max_servers + 1)), list(range(1, max_ushers + 1))]

    # set up the for loop using the iterator itertools.product
    for i in itertools.product(*combs):
        # setup seed and env
        random.seed(42)
        env = simpy.Environment()

        # setup the parameters for the current run
        num_cashiers, num_servers, num_ushers = i

        # run the sim
        env.process(run_theater(env, num_cashiers, num_servers, num_ushers, movgoers))
        env.run()

        # safe results per run
        stats_per_run.append([[num_cashiers, num_servers, num_ushers], statistics.mean(wait_times)])

        # clear wait_times for next iteration !
        wait_times.clear()

    # print the optimized configuration
    show_optimum_solution(stats_per_run, max_wait)


if __name__ == "__main__":
    main()
