import networkx as nx
import random

def solve(client):
    client.end()
    client.start()

    #if (client.v == client.bots):
    #    run_naive_MST(client)

    ram_method(client)


    client.end()

# Find the MST and remotes across the MST.
def run_naive_MST(client):
    MST_tree = nx.minimum_spanning_tree(client.G)

    postorder_list = list(nx.dfs_postorder_nodes(MST_tree, source=client.home))

    for v in range(len(postorder_list) - 1):
    	for v_e in range(v + 1, len(postorder_list)):
    		if (postorder_list[v], postorder_list[v_e]) in MST_tree.edges():
    			client.remote(postorder_list[v],postorder_list[v_e])

# This one is 4b on design doc
def run_naive_dijk(client):

    seenNodes = dict((node, False) for node in client.G.nodes) # dictionary with (int node, boolean) pairs
    botsAtNode = dict((node, -1) for node in client.G.nodes) # number of bots at each node (-1 for unseen nodes)
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

    for key in botsAtNode: # print all vertices with bots
        if botsAtNode[key] > 0:
            print(key,botsAtNode[key])

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
        # MAYBE TO BE CHANGED IF THIS DOES COST ANYTHING

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
