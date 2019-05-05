import networkx as nx
import random
import operator

def solve(client):
    client.end()
    client.start()

    #if (client.v == client.bots):
    #    run_naive_MST(client)

    # ram_method(client)

    if (client.k > 20):
        run_naive_MST(client)
    else:
        find_bots_scout(client)
    print(client.k)


    client.end()

# Find the MST and remotes across the MST.
def run_naive_MST(client):
    MST_tree = nx.minimum_spanning_tree(client.G)

    postorder_list = list(nx.dfs_postorder_nodes(MST_tree, source=client.home))

    for v in range(len(postorder_list) - 1):
    	for v_e in range(v + 1, len(postorder_list)):
    		if (postorder_list[v], postorder_list[v_e]) in MST_tree.edges():
    			client.remote(postorder_list[v], postorder_list[v_e])


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


def ram_method(client):
    studentWeights = {s: 1 for s in range(1, client.students + 1)} #How much to weight a student's opinion, 1 is default, 10000 is we know he is telling the truth, 0 is told truth V/2 many times.
    studentTruths = {s: 0 for s in range(1, client.students + 1)} #How many truths a student has said after verifying with remote
    studentLies = {s: 0 for s in range(1, client.students + 1)} #How many lies a student has said after verifying with remote
    studentOpinions = {node: list() for node in client.G.nodes} #dictionary between (node, and a list of student opinions)
    student_truth_teller = None; # This is the student who we will always believe if we know he must be correct.

    seenNodes = {node: False for node in client.G.nodes} # dictionary with (int node, boolean) pairs
    edge_list = []
    all_students = list(range(1, client.students + 1)) #A list of numbers indicating the students
    node_distance_to_home = {node: nx.dijkstra_path_length(client.G, node, client.home) for node in client.G.nodes if node != client.home} # Finds the distance of all nodes to home
    home_and_nodes_with_bots = [client.home] #These are all nodes that we would run dijkstra's to
    spt_nodes = {client.home} # States whether the current node is in the spt

    total_bots_found = 0

    # NAIVE: TO BE CHANGED SINCE COULD BE WASTEFUL TO SCOUT ALL VERTICES -- Scouts all vertices and updates stuentOpinions to hold all of their opinions.
    for node in client.G.nodes:
        if node == client.home:
            continue
        opinions_for_node = client.scout(node, all_students) #Returns a dictionary of student : opinion

        # TO BE CHANGED: The list index is one off of the student number since the student "1"'s opinion will be 0th in the list etc.
        #Move all opinions to the studentOpinions dictionary
        for s in all_students:
            curr_opinions = studentOpinions.get(node)
            studentOpinions.update({node: curr_opinions + [opinions_for_node.get(s)]}) #Add the student's opinion for the node

    # There are two stages to this algorithm.
    # First: We must build up a SPT. We do this by remoting using vertices outside of our SPT. We prefer vertices that use a lot of edges to connect to our current SPT,
    #        have a short edge connected to them, and have a high probability of containing a bot
    # Second: We must make choices at every iteration whether to keep on building up our SPT or to start remoting bots home along the SPT.
    # We switch to the second stage when the number of bots <= number of vertices in SPT

    # Note to self: We found distance to only closer nodes with bots. Would it be better or worse if we used distance to nodes in SPT

    #Implementing the first stage:
    while (client.bots - total_bots_found > len(spt_nodes)):
        for node in client.G.nodes:
            #You only want to remote using vertices outside of SPT
            if node in spt_nodes:
                continue






    home_and_nodes_with_bots = [client.home] + client.bot_locations

    print(studentOpinions)
    print(home_and_nodes_with_bots)

#NOTE: CHECK IF MY BOUNDS ARE CORRECT
def update_student_weights(client, studentWeights, studentTruths, studentLies, student_truth_teller):
    for student in studentWeights.keyList():
        if (studentLies.get(student) >= client.vertices / 2):
            studentWeights.update({student: 10000}) #this man is the truth teller
            student_truth_teller = student
        #elif studentTruths.get(student) > client.vertices / 2:
        #    studentWeights.update({student: 0}) #Everything else this man says can be a truth or a lie, therefore we know he is not useful
        else:
            #Weights students in a way such that the more lies a student has told, the more trustworthy his opinion
            studentWeights.update({student: studentLies.get(student) / (studentTruths.get(student) + studentLies.get(student))})


def find_bots_scout(client):

    all_students = list(range(1, client.students + 1))

    scoreAtNode = {node: 0 for node in client.G.nodes}
    non_home = list(range(1, client.home)) + list(range(client.home + 1, client.v + 1))
    studentVotes = {}
    for v in non_home:
        studentVotes = client.scout(v, all_students)
        for j in studentVotes.values():
            if(j == True):
                scoreAtNode[v] += 1
    sorted_scoreAtNode = sorted(scoreAtNode.items(), key=operator.itemgetter(1))[::-1]

    for nodeScore in sorted_scoreAtNode:
        myNode = nodeScore[0]
        pathHome = nx.dijkstra_path(client.G, myNode, client.home)
        for i in range(len(pathHome) - 1):
            if (client.bot_count[client.home] != client.l):
                vertex1 = pathHome[i]
                vertex2 = pathHome[i + 1]
                client.remote(vertex1, vertex2)
