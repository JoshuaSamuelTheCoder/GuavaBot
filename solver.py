# Put your solution here.

import networkx as nx
import random

def solve(client):
    client.end()    # terminate existing rescues
    client.start()  # retrieve an instance

    all_students = list(range(1, client.students + 1))
    print(all_students)
    non_home = list(range(1, client.home)) + list(range(client.home + 1, client.v + 1))
    print(client.v)
    print(client.home)
    print(non_home)
    client.scout(random.choice(non_home), all_students)

    for _ in range(100):
        u, v = random.choice(list(client.G.edges()))
        client.remote(u, v)


    client.end()    # terminate
