import networkx as nx
import random

def solve(client):
    client.end()
    client.start()

    if (client.v == client.bots):
        run_naive_MST(client)

    run_naive_dijk(client)


    client.end()

#This one just finds the MST and remotes across the MST.
def run_naive_MST(client):
    MST_tree = nx.minimum_spanning_tree(client.G)

    postorder_list = list(nx.dfs_postorder_nodes(MST_tree, source=client.home))

    for v in range(len(postorder_list) - 1):
    	for v_e in range(v + 1, len(postorder_list)):
    		if (postorder_list[v], postorder_list[v_e]) in MST_tree.edges():
    			client.remote(postorder_list[v],postorder_list[v_e])

#This one is 4b on design doc
def run_naive_dijk(client):
    #sorted_edge_list = print(client.G.edges())
    print(client.G.edgelist)
    #for edge in sorted_edge_list:
    #    print(edge)
