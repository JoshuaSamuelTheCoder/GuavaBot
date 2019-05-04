import networkx as nx
import random

def solve(client):
    client.end()
    client.start()

    if (client.v == client.bots):
        run_naive_MST(client)

    run_naive_dijk(client)


    client.end()

# Find the MST and remotes across the MST.
def run_naive_MST(client):
    MST_tree = nx.minimum_spanning_tree(client.G)

    postorder_list = list(nx.dfs_postorder_nodes(MST_tree, source=client.home))

    for v in range(len(postorder_list) - 1):
    	for v_e in range(v + 1, len(postorder_list)):
    		if (postorder_list[v], postorder_list[v_e]) in MST_tree.edges():
    			client.remote(postorder_list[v],postorder_list[v_e])


def find_bots_naive(client):
    """Helper for run_naive_dijk. Iterate through all edges, shortest -> longest,
        remoting across each edge twice.

        botsAtNode redundant bc client.bot_locations and client.bot_count.
    """
    seenNodes = {node: False for node in client.G.nodes} # dictionary with (int node, boolean) pairs
    botsAtNode = {node: -1 for node in client.G.nodes} # number of bots at each node (-1 for unseen nodes)
    edge_list = []

    for (vert1, vert2, weight) in client.G.edges.data('weight',default=1): # get triples of the form (int first vertex, int second vertex, int edge weight)
        edge_list.append((vert1, vert2, weight))

    sorted_edge_list = sorted(edge_list, key=lambda x:x[2]) # sort triples by edge weight

    for edge in sorted_edge_list:   # iterate through sorted edges
        if (False in seenNodes.values()): # if we still have unseen nodes
            vert1, vert2 = edge[0], edge[1]
            seenNodes[vert1], seenNodes[vert2] = True, True

            client.remote(vert1, vert2)
            botsAtNode[vert1] = client.remote(vert2, vert1)
            botsAtNode[vert2] = 0

    return botsAtNode


# This one is 4b on design doc
def run_naive_dijk(client):

    find_bots_naive(client)
    botLocations = client.bot_locations

    pathsHome = {}

    for botNode in botLocations:
        pathsHome[botNode] = (nx.dijkstra_path(client.G, botNode, client.home), nx.dijkstra_path_length(client.G, botNode, client.home))

    for i in range(len(botLocations)):
        startNode = botLocations[i]
        myPaths = {}

        for j in range(len(botLocations)):
            if (i != j):
                endNode = botLocations[j]
                myPaths[endNode] = (nx.dijkstra_path(client.G, startNode, endNode),
                    nx.dijkstra_path_length(client.G, startNode, endNode))

        print(myPaths)
