#Import libraries
import random
import simpy
import statistics

wait_times = []

class Cafe():
    def __init__(self, env, num_waiters, num_cookers):
        self.env = env
        self.waiter = simpy.Resource(env, num_waiters)
        self.cooker = simpy.Resource(env, num_cookers)

    def make_order(self, visitor):
        yield self.env.timeout(random.randint(3, 7)) #time that is needed to make an order

    def prepare_meal(self, visitor):
        yield self.env.timeout(random.randint(10, 30)) ##time that is needed to prepare a meal

def go_to_cafe(env, visitor, cafe):
    arrival_time = env.now

    #First make order
    with cafe.waiter.request() as request:
        yield request
        yield env.process(cafe.make_order(visitor))
    #Then cook the meal
    with cafe.cooker.request() as request:
        yield request
        yield env.process(cafe.prepare_meal(visitor))

    #Calculate wasiting time
    wait_times.append(env.now - arrival_time)


def run_cafe(env, num_waiters, num_cook):
    cafe = Cafe(env, num_waiters, num_cook)

    #Two visitors at the beginning
    for visitor in range(2):
        env.process(go_to_cafe(env, visitor, cafe))

    #Every 5 minutes new visitor comes
    while True:
        yield env.timeout(5)

        visitor += 1
        env.process(go_to_cafe(env, visitor, cafe))


#Calcultae average waiting time
def get_average_wait_time(wait_times):
    average_wait = statistics.mean(wait_times)
    minutes, frac_minutes = divmod(average_wait, 1)
    seconds = frac_minutes * 60
    return round(minutes), round(seconds)

#Input argument in function
def get_user_input():
    num_waiters = input("Input # of waiters working: ")
    num_cookers = input("Input # of cookers working: ")
    params = [num_waiters, num_cookers]
    if all(str(i).isdigit() for i in params):  # Check input is valid
        params = [int(x) for x in params]
    else:
        print(
            "Could not parse input. The simulation will use default values:",
            "\n1 waiter, 1 cooker.",
        )
        params = [1, 1]
    return params


def main():
    # Setup
    random.seed(42)
    num_waiters, num_cookers = get_user_input()

    # Run the simulation
    env = simpy.Environment()
    env.process(run_cafe(env, num_waiters, num_cookers))
    env.run(until=600)

    # View the results
    mins, secs = get_average_wait_time(wait_times)
    print(
        "Running simulation...",
        f"\nThe average wait time is {mins} minutes and {secs} seconds.",
    )

if __name__ == '__main__':
    main()
