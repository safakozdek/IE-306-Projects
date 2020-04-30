import simpy
import random
import numpy as np

"""
Collect and report statistics on:
o Utilization of the answering system.
o Utilization of the operators,
o Average Total Waiting Time
o Maximum Total Waiting Time to Total System Time Ratio,
o Average number of people waiting to be served by each operator.
o Average number of customers leaving the system unsatisfied either due to
incorrect routing or due to long waiting times.
"""

END_TIME = 0
SYSTEM_UTIL = 0
OPERATORS_UTIL = 0
AVG_TOTAL_WAITING = 0
MAX_TOTAL_WAITING = 0
MAX_TOTAL_SYSTEM_TIME = 0
AVG_WAITING_PEOPLE = 0
AVG_UNSATISFIED_PEOPLE = 0
# --------
NUMBER_OF_CALLS = 1000
CALL_CAPACITY = 100  # Call capacity that auto answering system can handle at the same time.

INTERARRIVAL_RATE = 6
TAKE_RECORD_MEAN = 5
OPERATOR_BREAKS = [0, 0, 0]  # index 0 is empty all the time.
MAX_Q_WAIT_TIME = 10

"""
Arrivals:
Exponential interarrival times, mean = 6
The answering system can serve 100 callers simultaneously (100 parallel channels). When
all channels are busy it drops any incoming call without answering.
---
Take records:
exponential , mean = 5
---
Routing:
0.3 - Operator 1
0.7 - Operator 2
After
0.1 chance of misrouting 
A caller that is routed to the wrong operator hangs up immediately. 
-- Burada unsatisfied olarak ayrıldı ve q'ya dahil olmadı sanırım. --
---
Waiting Q: 
FCFS 
2 different q's for 2 operators
An arriving customer that has been waiting on hold for 10 minutes hangs up and leaves
the system (reneging). -- Unsatisfaction ++  --
---
Service:
Op1 - LogNormally distributed with mean 12 minutes and standard deviation 6 minutes
Op2 - uniformly distributed between 1 and 7 minutes.
---
Operator Breaks:
When an operator decides to take a break, he/she waits until completing all the customers already waiting
for her/him. -- Until q is empty or until surving the last person at q ??? ---
If new customers arrive during operators break, they wait in the q
The number of breaks an operator wishes to take during an 8-hour shift is known to be
distributed according to a Poisson distribution with a mean of 8 breaks per shift. -- 1 per hour--
"""


class Call():
    current_call = 0
    total_call_success = 0
    total_call_fail = 0

    def __init__(self, id, env, operator1, operator2):
        self.id = id
        self.env = env
        self.operators = [None, operator1, operator2]  # index 0 is empty
        self.arrival_t = self.env.now
        self.action = env.process(self.call())

    def call(self):

        if Call.current_call >= CALL_CAPACITY:  # this might not be included in statistics (like fail calls)
            # Answering system is full, drop the call.
            print("Call{} has been dropped.(Capacity reached)".format(self.id))
            Call.total_call_fail += 1
            yield env.process(self.check_end())
            return

        # Take Customer Info (Record)
        Call.current_call += 1
        yield env.timeout(random.expovariate(1.0 / TAKE_RECORD_MEAN))
        Call.current_call -= 1

        operator_random = random.randint(0, 9)
        fault_random = random.randint(0, 9)

        if fault_random == 0:  # %10
            print("Call{} has been dropped.(Wrong routing)".format(self.id))
            Call.total_call_fail += 1
            yield env.process(self.check_end())
            return

        yield env.process(self.service(1 if operator_random < 3 else 2))

    def check_end(self):
        if Call.total_call_success + Call.total_call_fail == NUMBER_OF_CALLS:  # termination
            yield env.process(self.end())

    def service(self, operator_id):
        with self.operators[operator_id].request() as req:
            q_arrival = env.now
            yield req
            q_waiting = env.now - q_arrival

            if q_waiting < MAX_Q_WAIT_TIME:
                print("Call{} -> operator {}".format(self.id, operator_id))
                yield self.env.process(self.serve(operator_id))
            else:
                print("Call{} has been dropped.(Waited too much in queue)".format(self.id))
                Call.total_call_fail += 1

    def serve(self, operator_id):
        if operator_id == 1:
            # Calculate mu and sigma for lognormal distribution mean = 12, std = 6
            mean, std = 12, 6
            m, sig = self.get_lognormal_values(mean, std)
            yield env.timeout(random.lognormvariate(sigma=sig, mu=m))

        else:
            rand_time = random.uniform(1, 7)
            yield env.timeout(rand_time)

        print("Call{} has been served by operator {}".format(self.id, operator_id))
        Call.total_call_success += 1

        yield env.process(self.check_end())
        yield env.process(self.check_break(operator_id))

    def get_lognormal_values(self, mean, std):
        phi = (std ** 2 + mean ** 2) ** 0.5
        mu = np.log(mean ** 2 / phi)
        sigma = (np.log(phi ** 2 / mean ** 2)) ** 0.5
        return mu, sigma

    def check_break(self, operator_id):
        q_length = len(self.operators[operator_id].queue)

        if OPERATOR_BREAKS[operator_id] > 0 and q_length == 0:
            OPERATOR_BREAKS[operator_id] -= 1
            print("Operator{} leaves for a break".format(operator_id))
            yield env.timeout(3)
            print("Operator{} returned from break".format(operator_id))
            if OPERATOR_BREAKS[operator_id] != 0:  # might take multiple breaks back to back.
                yield env.process(self.check_break(operator_id))

        return None

    def end(self):
        global END_TIME
        END_TIME = self.env.now
        self.action.interrupt()
        yield self.env.timeout(0)


def call_generator(env, operator1, operator2):
    for i in range(NUMBER_OF_CALLS):
        yield env.timeout(random.expovariate(1.0 / INTERARRIVAL_RATE))
        print("Incomig Call{}".format(i))
        Call((i + 1), env, operator1, operator2)


def break_generator(env, operator_id):
    rate = 60  # 1 in every 60 minutes
    while True:
        yield env.timeout(random.expovariate(1.0 / rate))
        OPERATOR_BREAKS[operator_id] += 1


if __name__ == "__main__":
    env = simpy.Environment()
    operator1 = simpy.Resource(env, capacity=1)
    operator2 = simpy.Resource(env, capacity=1)
    env.process(call_generator(env, operator1, operator2))
    env.process(break_generator(env, 1))
    env.process(break_generator(env, 2))

    try:
        env.run()
    except simpy.Interrupt as interrupt:
        print("END")
