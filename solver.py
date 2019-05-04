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

    pathsHome = {} # dictionary of form {node with bot: (path home as list of vertices, distance home)}

    for botNode in botLocations: # find path from each node to home, add to pathsHome
        pathsHome[botNode] = (nx.dijkstra_path(client.G, botNode, client.home),
        nx.dijkstra_path_length(client.G, botNode, client.home))

    print(pathsHome)

    for startNode in botLocations: # find potential shorter paths between nodes with bots
        for midNode in pathsHome:
            if (startNode != midNode):
                newPathLength = nx.dijkstra_path_length(client.G, startNode, midNode)

                # if startNode->endNode->home shorter than startNode->home, update pathsHome[startNode] = (just startNode->endNode path, dist(startNode->endNode->home))
                if (pathsHome[startNode][1] > newPathLength + pathsHome[midNode][1]):
                    pathsHome[startNode] = (nx.dijkstra_path(client.G, startNode, midNode), newPathLength + pathsHome[midNode[1]])

    # construct shortestPathsTree from pathsHome
    shortestPathsTree = nx.Graph()

    # add each node from pathsHome paths
    for node in pathsHome:
        myPath = pathsHome[node][0]
        for myNode in myPath:
            shortestPathsTree.add_node(myNode)

    # add each edge from pathsHome paths
    for node in pathsHome:
        myPath = pathsHome[node][0]
        for i in range(len(myPath) - 1):
            shortestPathsTree.add_edge(myPath[i], myPath[i+1])

    # postorder SPT to remote bots home
    postorder_SPT = list(nx.dfs_postorder_nodes(shortestPathsTree, source=client.home))

    # remote bots home
    for v in range(len(postorder_SPT) - 1):
    	for v_e in range(v + 1, len(postorder_SPT)):
    		if (postorder_SPT[v], postorder_SPT[v_e]) in shortestPathsTree.edges():
    			client.remote(postorder_SPT[v],postorder_SPT[v_e])

    print(pathsHome)
    print(postorder_SPT)
