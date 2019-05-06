import networkx as nx
import random
import operator
import math

def solve(client):
    client.end()
    client.start()

    ram_method(client)

    # run_naive_dijk(client)

    """
    if (client.k > 20):
        run_naive_MST(client)
    else:
        find_bots_scout(client)
    print(client.k)
    """


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
    spt_nodes = []
    spt_edges = []

    for botNode in botLocations: # find path from each node to home, add to pathsHome
        pathsHome[botNode] = (nx.dijkstra_path(client.G, botNode, client.home),
        nx.dijkstra_path_length(client.G, botNode, client.home))


    print("pathsHome:", pathsHome)

    sorted_startNodes = sorted(pathsHome, key=lambda k: pathsHome[k][1]) # sort pathsHome by distance from each bot node to home
    print("sorted_startNodes:", sorted_startNodes)

    closestbotNode = sorted_startNodes[0] # bot node with shortest path to home

    for node in pathsHome[closestbotNode][0]: # add into SPT all nodes from closestbotNode->home
        spt_nodes.append(node)

    for i in range(len(pathsHome[closestbotNode][0]) - 1): # add into SPT all edges from closestbotNode->home
        spt_edges.append((pathsHome[closestbotNode][0][i], pathsHome[closestbotNode][0][i + 1]))

    print("spt_nodes initial:", spt_nodes)
    print("spt_edges initial:",spt_edges)

    for i in range(1, len(sorted_startNodes)): # for each remaining bot node
        startNode = sorted_startNodes[i]
        pathsToSPT = {}

        pathsToSPT[client.home] = (nx.dijkstra_path(client.G, startNode, client.home), nx.dijkstra_path_length(client.G, startNode, client.home))
        for spt_node in spt_nodes: # compute (path, path length) from bot node to spt_node
            pathsToSPT[spt_node] = (nx.dijkstra_path(client.G, startNode, spt_node), nx.dijkstra_path_length(client.G, startNode, spt_node))

        sorted_pathsToSPT = sorted(pathsToSPT, key=lambda k: pathsToSPT[k][1])
        print("pathsToSPT:", pathsToSPT)
        print("sorted_pathsToSPT:", sorted_pathsToSPT)

        closest_spt_node = sorted_pathsToSPT[0] # closest node in SPT

        # add path to spt_nodes and spt_edges
        pathToSPT = pathsToSPT[closest_spt_node][0]
        for node in pathToSPT:
            spt_nodes.append(node)
        for i in range(len(pathToSPT) - 1):
            spt_edges.append((pathToSPT[i], pathToSPT[i + 1]))

        print("spt_nodes:", spt_nodes)
        print("spt_edges:", spt_edges)

    #build shortestPathsTree from spt_nodes and spt_edges
    shortestPathsTree = nx.Graph()
    for spt_node in spt_nodes:
        shortestPathsTree.add_node(spt_node)
    for spt_edge in spt_edges:
        shortestPathsTree.add_edge(spt_edge[0], spt_edge[1])

    # postorder SPT to remote bots home
    postorder_SPT = list(nx.dfs_postorder_nodes(shortestPathsTree, source=client.home))

    # remote bots home
    for v in range(len(postorder_SPT) - 1):
    	for v_e in range(v + 1, len(postorder_SPT)):
    		if (postorder_SPT[v], postorder_SPT[v_e]) in shortestPathsTree.edges():
    			client.remote(postorder_SPT[v],postorder_SPT[v_e])




    """# add each edge from closest node in sorted_paths
    myPath = sorted_startNodes[0][0]
    for i in range(len(myPath) - 1):
        spt_nodes.append(myPath[i], myPath[i+1])

    print(spt_nodes)



    for i in range(1, len(sorted_startNodes)):
        myNode = sorted_startNodes[1]



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
"""


def ram_method(client):
    all_students = list(range(1, client.students + 1)) #A list of numbers indicating the students
    # Limit sampling to 30 students
    if (len(all_students) > 20):
        all_students = random.sample(all_students, k=20)
    studentWeights = {s: 1.0 for s in all_students} #How much to weight a student's opinion, 1 is default, 10000 is we know he is telling the truth, 0 is told truth V/2 many times.
    studentTruths = {s: 0 for s in all_students} #How many truths a student has said after verifying with remote
    studentLies = {s: 0 for s in all_students} #How many lies a student has said after verifying with remote
    studentOpinions = {node: {student:0 for student in all_students} for node in client.G.nodes} #dictionary between (node, and a list of student opinions)
    student_truth_teller = None; # This is the student who we will always believe if we know he must be correct.

    seenNodes = {node: False for node in client.G.nodes} # dictionary with (int node, boolean) pairs
    edge_list = []
    node_distance_to_home = {node: nx.dijkstra_path_length(client.G, node, client.home) for node in client.G.nodes} # Finds the distance of all nodes to home
    home_and_nodes_with_bots = [client.home] #These are all nodes that we would run dijkstra's to
    spt_nodes = [client.home] # States whether the current node is in the spt

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
            curr_opinions.update({s: opinions_for_node.get(s)})
            studentOpinions.update({node: curr_opinions}) #Add the student's opinion for the node

    # There are two stages to this algorithm.
    # First: We must build up a SPT. We do this by remoting using vertices outside of our SPT. We prefer vertices that use a lot of edges to connect to our current SPT,
    #        have a short edge connected to them, and have a high probability of containing a bot
    # Second: We must make choices at every iteration whether to keep on building up our SPT or to start remoting bots home along the SPT.
    # We switch to the second stage when the number of bots <= number of vertices in SPT

    # Note to self: We now find distance to nodes in SPT because we update SPT first using closer nodes than using farther nodes
    # TODO: Also case where number of remaining bots is equal to the number of unknown vertices.

    #Implementing the first stage:
    remoted_nodes_first_stage = set() # Set of remoted nodes
    shortestPathsTree = None
    #while(len(spt_nodes) + len(remoted_nodes_first_stage) < len(client.G.nodes)):
    while (client.bots - total_bots_found > len(spt_nodes) - 1):
        #if student_truth_teller != null:
        #   run_spt()
        best_node, neighbor_node = find_best_node_and_neighbor(client, spt_nodes, remoted_nodes_first_stage, studentOpinions, studentWeights)
        # Get the number of bots remoted
        #print("Nodes:", best_node, neighbor_node)
        num_bots_remoted = client.remote(best_node, neighbor_node)
        total_bots_found += num_bots_remoted

        # Don't ever remote from this node again (at least in this step)
        remoted_nodes_first_stage.add(best_node)

        #print(studentOpinions.get(best_node))
        #Update whether the student told the truth or not
        for student in studentTruths:
            # Wow this is gross but it's because the first student is 0 indexed etc.
            if studentOpinions.get(best_node) == None:
                break
            #print(student)
            if (num_bots_remoted >= 1 and studentOpinions.get(best_node).get(student)) or (num_bots_remoted == 0 and not studentOpinions.get(best_node).get(student)):
                studentTruths.update({student: studentTruths.get(student) + 1})
            else:
                studentLies.update({student: studentLies.get(student) + 1})

        # Now update the student weights
        update_student_weights(client, studentWeights, studentTruths, studentLies, student_truth_teller)

        #Brian's code
        botLocations = client.bot_locations
        botLocations = botLocations + [client.home] #Have to add home because we suck
        pathsHome = {} # dictionary of form {node with bot: (path home as list of vertices, distance home)}
        spt_nodes = []
        spt_edges = []

        # Make Brian tree will fill in everything so passing in parameters to be filled
        shortestPathsTree = make_brian_graph(client, pathsHome, spt_nodes, spt_edges, botLocations)

    #This is the second part of the algorithm

    print("Second part!")
    remoted_from_nodes = remoted_nodes_first_stage
    # postorder SPT to remote bots home
    # While you still have more bots to remote home keep remoting
    while (client.bot_count[client.home] < client.bots):
        if (not should_remote_spt(client, studentOpinions, studentWeights, spt_nodes, remoted_from_nodes, client.bots - total_bots_found) and not len(spt_nodes) + len(remoted_from_nodes) >= client.v):
            best_node, neighbor_node = find_best_node_and_neighbor(client, spt_nodes, remoted_nodes_first_stage, studentOpinions, studentWeights)
            #print("LENGTH:", len(spt_nodes), len(remoted_from_nodes))
            # Get the number of bots remoted
            #print("Best Node", best_node, neighbor_node)
            num_bots_remoted = client.remote(best_node, neighbor_node)
            total_bots_found += num_bots_remoted

            # Don't ever remote from this node again (at least in this step)
            remoted_from_nodes.add(best_node)

            #Update whether the student told the truth or not
            for student in studentTruths:
                # Wow this is gross but it's because the first student is 0 indexed etc.
                if studentOpinions.get(best_node) == None: #Maybe this is home and somehow it fell through the cracks.
                    break
                if (num_bots_remoted == 1 and studentOpinions.get(best_node).get(student)) or (num_bots_remoted == 0 and not studentOpinions.get(best_node).get(student)):
                    studentTruths.update({student: studentTruths.get(student) + 1})
                elif (num_bots_remoted > 1):
                    print("ERROR!!!!!")
                    print("ERROR!!!!!")
                    print("ERROR!!!!!")
                    print("ERROR!!!!!")
                    print("ERROR!!!!!")
                else:
                    studentLies.update({student: studentLies.get(student) + 1})

            # Now update the student weights
            update_student_weights(client, studentWeights, studentTruths, studentLies, student_truth_teller)

            #Brian's code
            botLocations = client.bot_locations
            botLocations = botLocations + [client.home] #Have to add home because we suck
            pathsHome = {} # dictionary of form {node with bot: (path home as list of vertices, distance home)}
            spt_nodes = []
            spt_edges = []

            # Make Brian tree will fill in everything so passing in parameters to be filled
            shortestPathsTree = make_brian_graph(client, pathsHome, spt_nodes, spt_edges, botLocations)
        else:
            print("Moving SPT")
            #Brian's code
            botLocations = client.bot_locations
            botLocations = botLocations + [client.home] #Have to add home because we suck
            pathsHome = {} # dictionary of form {node with bot: (path home as list of vertices, distance home)}
            spt_nodes = []
            spt_edges = []

            # Make Brian tree will fill in everything so passing in parameters to be filled
            shortestPathsTree = make_brian_graph(client, pathsHome, spt_nodes, spt_edges, botLocations)

            postorder_SPT = list(nx.dfs_postorder_nodes(shortestPathsTree, source=client.home))

            #TODO: Make it so students update weights if they are wrong when remoting
            #TODO: CHANGE IT SO IT DOESN'T JUST FINISH UP THE GRAPH
            # remote bots home
            print("start remoting home")
            v = 0
            for v_e in range(v + 1, len(postorder_SPT)):
                more_bots_found = 0
                if (postorder_SPT[v], postorder_SPT[v_e]) in shortestPathsTree.edges():
                    more_bots_found = -client.bot_count[postorder_SPT[v]] + client.remote(postorder_SPT[v],postorder_SPT[v_e]) #client.bot_count must come first because it would change!
                    total_bots_found += more_bots_found
                for student in studentTruths:
                    # Wow this is gross but it's because the first student is 0 indexed etc.
                    if studentOpinions.get(postorder_SPT[v]) == None: #Maybe this is home and somehow it fell through the cracks.
                        break
                    if (more_bots_found == 1 and studentOpinions.get(postorder_SPT[v]).get(student)) or (more_bots_found == 0 and not studentOpinions.get(postorder_SPT[v]).get(student)):
                        studentTruths.update({student: studentTruths.get(student) + 1})
                    elif (more_bots_found > 1):
                        print("ERROR!!!!!")
                        print("ERROR!!!!!")
                        print("ERROR!!!!!")
                        print("ERROR!!!!!")
                        print("ERROR!!!!!")
                    else:
                        studentLies.update({student: studentLies.get(student) + 1})
            print("done remoting home")




def make_brian_graph(client, pathsHome, spt_nodes, spt_edges, botLocations):
    for botNode in botLocations: # find path from each node to home, add to pathsHome
        pathsHome[botNode] = (nx.dijkstra_path(client.G, botNode, client.home),
        nx.dijkstra_path_length(client.G, botNode, client.home))

    sorted_startNodes = sorted(pathsHome, key=lambda k: pathsHome[k][1]) # sort pathsHome by distance from each bot node to home

    closestbotNode = sorted_startNodes[0] # bot node with shortest path to home

    for node in pathsHome[closestbotNode][0]: # add into SPT all nodes from closestbotNode->home
        spt_nodes.append(node)

    for i in range(len(pathsHome[closestbotNode][0]) - 1): # add into SPT all edges from closestbotNode->home
        spt_edges.append((pathsHome[closestbotNode][0][i], pathsHome[closestbotNode][0][i + 1]))

    #print("spt_nodes initial:", spt_nodes)
    #print("spt_edges initial:",spt_edges)

    for i in range(1, len(sorted_startNodes)): # for each remaining bot node
        startNode = sorted_startNodes[i]
        pathsToSPT = {}

        pathsToSPT[client.home] = (nx.dijkstra_path(client.G, startNode, client.home), nx.dijkstra_path_length(client.G, startNode, client.home))
        for spt_node in spt_nodes: # compute (path, path length) from bot node to spt_node
            pathsToSPT[spt_node] = (nx.dijkstra_path(client.G, startNode, spt_node), nx.dijkstra_path_length(client.G, startNode, spt_node))

        sorted_pathsToSPT = sorted(pathsToSPT, key=lambda k: pathsToSPT[k][1])
        #print("pathsToSPT:", pathsToSPT)
        #print("sorted_pathsToSPT:", sorted_pathsToSPT)

        closest_spt_node = sorted_pathsToSPT[0] # closest node in SPT

        # add path to spt_nodes and spt_edges
        pathToSPT = pathsToSPT[closest_spt_node][0]
        for node in pathToSPT:
            spt_nodes.append(node)
        for i in range(len(pathToSPT) - 1):
            spt_edges.append((pathToSPT[i], pathToSPT[i + 1]))

        #print("spt_nodes:", spt_nodes)
        #print("spt_edges:", spt_edges)

    #build shortestPathsTree from spt_nodes and spt_edges
    shortestPathsTree = nx.Graph()
    for spt_node in spt_nodes:
        shortestPathsTree.add_node(spt_node)
    for spt_edge in spt_edges:
        shortestPathsTree.add_edge(spt_edge[0], spt_edge[1])

    return shortestPathsTree


#NOTE: CHECK IF MY BOUNDS ARE CORRECT
def update_student_weights(client, studentWeights, studentTruths, studentLies, student_truth_teller):
    # If there is already a truth teller, no need to update
    #print(studentLies)
    if student_truth_teller != None:
        return
    for student in studentWeights:
        if (studentLies.get(student) >= client.v / 2):
            studentWeights.update({student: 10000}) #this man is the truth teller
            student_truth_teller = student
            #If there is a truth teller than you should just listen to him.
            for student in studentWeights:
                if student != student_truth_teller:
                    studentWeights.update({student: 0})
            return
        #elif studentTruths.get(student) > client.vertices / 2:
        #    studentWeights.update({student: 0}) #Everything else this man says can be a truth or a lie, therefore we know he is not useful
        else:
            #Weights students in a way such that the more lies a student has told, the more trustworthy his opinion
            #studentWeights.update({student: 1.0 + studentLies.get(student) / (client.v / 20 + studentTruths.get(student) + studentLies.get(student))})
            #studentWeights.update({student: 1.0 + studentLies.get(student) / (client.v / 4.0)})
            #studentWeights.update({student: 1.0})
            studentWeights.update({student: 1.055 ** studentLies.get(student)}) #TO LOOK AT


def find_hueristic_value(client, node, studentOpinions, studentWeights, nodes_to_spt):
    total_hueristic = 0
    for student in studentWeights:
        if studentOpinions.get(node).get(student):
            #if random.randint(1,101) >= 20: #TO LOOK AT
            total_hueristic += studentWeights.get(student) #TO LOOK AT

    total_hueristic += len(nodes_to_spt) * 0.01 * client.students #TO LOOK AT
    #total_hueristic -= (client.G.get_edge_data(node, nodes_to_spt[1]).get('weight') * len(studentWeights) / 4000.0) #TO LOOK AT
    return total_hueristic


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

def find_best_node_and_neighbor(client, spt_nodes, remoted_nodes_first_stage, studentOpinions, studentWeights):
    best_node = None # We will choose the best node
    neighbor_node = None # We will remote to this node, first node on way to SPT
    best_hueristic_seen = float("-inf")# Keep track of the best hueristic value seen
    #print(spt_nodes)

    for node in client.G.nodes:
        #You only want to remote using vertices outside of SPT
        if node in spt_nodes or node in remoted_nodes_first_stage:
            continue

        #print(node)
        # Find the shortest path to the SPT and the nodes along the path
        shortest_path_to_spt = math.inf
        best_path_nodes_to_spt = list()

        for spt_node in spt_nodes:
            distance_to_spt_node = nx.dijkstra_path_length(client.G, node, spt_node)
            nodes_on_path_to_spt_node = nx.dijkstra_path(client.G, node, spt_node)
            if (distance_to_spt_node <= shortest_path_to_spt):
                # Only update the path if it is either shorter or if it is equal and contains more nodes
                if (distance_to_spt_node < shortest_path_to_spt or len(nodes_on_path_to_spt_node) > len(best_path_nodes_to_spt)):
                    shortest_path_to_spt = distance_to_spt_node
                    best_path_nodes_to_spt = nodes_on_path_to_spt_node # List of nodes on the path

        #Find the hueristic value for the current node
        hueristic_for_node = find_hueristic_value(client, node, studentOpinions, studentWeights, best_path_nodes_to_spt)

        # TO BE CHANGED -- Maybe we can improve this, right now am just only updating the best node if it has at least the same hueristic, not handling ties well
        if hueristic_for_node >= best_hueristic_seen:
            best_hueristic_seen = hueristic_for_node
            best_node = node
            neighbor_node = best_path_nodes_to_spt[1] #First node on the path
    # After finding the best node and its neighbor to remote to, return them
    return best_node, neighbor_node


# Returns true if you should start remoting home along SPT, false otherwise
def should_remote_spt(client, studentOpinions, studentWeights, spt_nodes, remoted_from_nodes, num_bots_remaining):
    """
    hueristic_contains_bot = list()
    for node in client.G.nodes:
        if node == client.home:
            continue
        total_hueristic_node = 0
        for student in studentWeights:
            if studentOpinions.get(node)[student]:
                total_hueristic_node += studentWeights.get(student)
        hueristic_contains_bot += [(node, total_hueristic_node)]
    sorted(hueristic_contains_bot, key=lambda k: k[1])

    for i in range(0, 1):
    #for i in range(0, 1):
        if hueristic_contains_bot[i][0] not in spt_nodes:
            return False

    return True
    """

    if num_bots_remaining == 0:
        return True

    hueristic_spt = 0
    hueristic_outside = 0
    for node in client.G.nodes:
        if node == client.home or node in remoted_from_nodes:
            continue
        total_hueristic_node = 0
        for student in studentWeights:
            #if random.randint(1,101) >= 40:
            if studentOpinions.get(node).get(student):
                if node in spt_nodes:
                    hueristic_spt += studentWeights.get(student)
                else:
                    hueristic_outside += studentWeights.get(student)
    return hueristic_spt > num_bots_remaining * 0.4 * hueristic_outside / (client.v - len(remoted_from_nodes)) #TO LOOK AT

    """all_students = list(range(1, client.students + 1))


    scoreAtNode = {node: 0 for node in client.G.nodes}
    non_home = list(range(1, client.home)) + list(range(client.home + 1, client.v + 1))
    dic = {}
    for v in non_home:
    	dic = client.scout(v, all_students)
    	for j in dic.values():
    		if(j == True):
    			scoreAtNode[v] += 1

    sorted_scoreAtNode = sorted(scoreAtNode.items(), key=operator.itemgetter(1))[::-1]

    print(sorted_scoreAtNode)"""


	#pathsHome = {}

	#for botNode in sorted_scoreAtNode:
	#	pathsHome[botNode] = (nx.dijkstra_path(client.G, botNode, client.home),
    #   nx.dijkstra_path_length(client.G, botNode, client.home))


	#pathsHome = {}

	#for botNode in sorted_scoreAtNode:
	#	pathsHome[botNode] = (nx.dijkstra_path(client.G, botNode, client.home),
    #   nx.dijkstra_path_length(client.G, botNode, client.home))
