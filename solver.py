<<<<<<< HEAD
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
=======
def solve(client):
    client.end()
    client.start()

    MST_tree = nx.minimum_spanning_tree(client.G)

    preorder_list = list(nx.dfs_preorder_nodes(MST_tree, source=client.home))[::-1]


    for v in range(len(preorder_list) - 1):
    	for v_e in range(v, len(preorder_list)):
    		if(preorder_list[v], preorder_list[v_e]) in MST_tree.edges():
    			client.remote(preorder_list[v],preorder_list[v_e])

    client.end()
>>>>>>> f6ab5928e0d4b1b1a9db3d06c5520ae03c9f2df2
