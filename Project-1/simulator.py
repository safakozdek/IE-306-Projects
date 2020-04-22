import simpy
import random

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

SYSTEM_UTIL = 0
OPERATORS_UTIL = 0
AVG_TOTAL_WAITING = 0
MAX_TOTAL_WAITING = 0
MAX_TOTAL_SYSTEM_TIME = 0
AVG_WAITING_PEOPLE = 0
AVG_UNSATISFIED_PEOPLE = 0

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

    def __init__(self, id, env, operator1, operator2):
        self.id = id
        self.env = env
        self.operator1 = operator1
        self.operator2 = operator2
        self.arrival_t = self.env.now
        self.action = env.process(self.call())

    def call(self):
        """
        TODO: Burada bütün call processi olacak.
        :return:
        """



class Break():

    def __init__(self, id, env, operator):
        self.id = id
        self.env = env
        self.operator = operator
        self.starting_t = self.env.now
        self.action = env.process(self.go_break())

    def go_break(self):
        break_time = 0 # random sanırım
        with self.operator.request() as req:
            yield req # Wait for access
            yield env.timeout(break_time)



def call_generator(env, operator):
    """Generate new cars that arrive at the gas station."""
    for i in range(10):
        INTERARRIVAL_RATE = 6
        yield env.timeout(random.expovariate(INTERARRIVAL_RATE))
        call = Call((i+1), env, operator)


def break_generator(env, operator):
    rate = 0
    counter = 1
    while True:
        yield env.timeout(random.expovariate(rate)) # poisson bir çeşit expovariate olarak ifade edilebiliyor olmalı
        operator_break = Break(counter, env, operator)
        counter += 1




if __name__ == "__main__":

    env = simpy.Environment()
    operator1 = simpy.Resource(env, capacity=1)
    operator2 = simpy.Resource(env, capacity=1)
    env.process(call_generator(env, operator1, operator2))
    env.process(break_generator(env, operator1))
    env.process(break_generator(env, operator2))