import networkx as nx
import random

def solve(client):
    client.end()
    client.start()
    
    MST_tree = nx.minimum_spanning_tree(client.G)

    preorder_list = list(nx.dfs_preorder_nodes(MST_tree, source=client.home))[::-1]

    for v in range(len(preorder_list) - 1):
    	for v_e in range(v + 1, len(preorder_list)):
    		if (preorder_list[v], preorder_list[v_e]) in MST_tree.edges():
    			client.remote(preorder_list[v],preorder_list[v_e])



    client.end()
