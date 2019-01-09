import networkx as nx
import random
import numpy.random as rand
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import statistics
import csv



def make_nodes(G, n_nodes):
    G.add_nodes_from(range(n_nodes))
    for node in list(G.nodes):
        G.nodes[node]["tie"] = 1

def normal_rand_edges(G, mean=5, sd=2):
    nodes = list(G.nodes)
    for parent_node in nodes:
        connections = max([1, round(rand.normal(mean, sd))])
        connected = len(list(G.adj[parent_node]))

        while connected < connections:
            edge_node = random.choice(nodes)
            if edge_node != parent_node:
                G.add_edge(parent_node, edge_node)
                connected += 1

def add_influencer(G, influencer_prop):
    current_nodes = len(list(G.nodes))
    id = len(list(G.nodes))
    G.add_node(id)
    G.nodes[id]["tie"] = 1
    for node in range(current_nodes):
        if random.random() < influencer_prop:
            G.add_edge(id, node)
    return id

def draw(G, pos, number):
    #Assign colors
    color_map = []
    for node in list(G.nodes):
        if G.nodes[node]["tie"] == 1 and node != influencer_id:
            color_map.append('grey')
        elif G.nodes[node]["tie"] == 1 and node == influencer_id:
            color_map.append('#F08080')
        elif G.nodes[node]["tie"] == 0 and node == influencer_id:
            color_map.append('#800000')
        else:
            color_map.append('black')
    #draw the graph
    plt.plot()
    nx.draw(G, pos = pos, node_color = color_map, with_labels=False)
    path = "results/tie_{0}".format(number)
    plt.savefig(path)

def def_assess_changes(G, tie_utility_loss):
    nodes = list(G.nodes)
    switch_status = []
    for node in nodes:
        node_tie = G.nodes[node]["tie"]
        #Get adjacent nodes
        adj = list(G.adj[node])
        tie_status = []
        for adj_node in adj:
            tie_status.append(G.nodes[adj_node]["tie"])
        if len(tie_status) > 0:
            mean_tie_usage = sum(tie_status)/len(tie_status)
        else:
            mean_tie_usage = 0
        #Get conformity: 0 = perfect conformity, 1 = perfectly unique
        current_conformity_utility = 1 - abs(node_tie - mean_tie_usage)
        alternative_conformity_utility = abs(node_tie - mean_tie_usage) #conformity utility if switch tie status tomorrow, cetris parabus
        if node_tie == 1:
            current_utility = current_conformity_utility - tie_utility_loss
            alternative_utility = alternative_conformity_utility
        else:
            current_utility = current_conformity_utility
            alternative_utility = alternative_conformity_utility - tie_utility_loss
        #assess whether to switch tomorrow or not
        if current_utility < alternative_utility:
            #Only switch if the alternative is better than the current
            switch = True
        else:
            switch = False
        switch_status.append(switch)
    return switch_status

def switch(G, switch_status):
    for node_id in range(len(switch_status)):
        switch = switch_status[node_id]
        if switch and G.nodes[node_id]["tie"] == 1:
            G.nodes[node_id]["tie"] = 0
        elif switch and G.nodes[node_id]["tie"] == 0:
            G.nodes[node_id]["tie"] = 1

def get_stats(G):
    count = 0
    tie_count = 0
    connections = []
    for node in list(G.nodes):
        count += 1
        tie_count += G.nodes[node]["tie"]
        connections.append(len(list(G.adj[node])))
    stats = {}
    stats["count"] = count
    stats["tie_prop"] = tie_count / count
    stats["mean_connections"] = statistics.mean(connections)
    stats["sd_connections"] = statistics.stdev(connections)
    return stats

def run_sim(n_nodes_list, days, iter, tie_util_range, influencer_range, mean_connections, sd_connections):
    data = []
    total_sims = len(n_nodes_list)*iter*len(tie_util_range)*len(influencer_range)*len(mean_connections)*len(sd_connections)
    sim = 0
    print("total simulations: {0}".format(total_sims))
    for n_nodes in n_nodes_list:
        for tie_utility_loss in tie_util_range:
            for influencer_prop in influencer_range:
                for mean in mean_connections:
                    for sd in sd_connections:
                        for i in range(iter):
                            sim += 1
                            G = nx.Graph()

                            make_nodes(G, n_nodes)
                            normal_rand_edges(G, mean=mean, sd=sd)
                            influencer_id = add_influencer(G, influencer_prop)
                            stats = []
                            switch_status = def_assess_changes(G, tie_utility_loss)
                            for day in range(days):
                                #Make change based on previous day
                                switch(G, switch_status)
                                DAY = day+1
                                if DAY == 1:
                                    #change tie pref
                                    G.nodes[influencer_id]["tie"] = 0
                                #assess day
                                switch_status = def_assess_changes(G, tie_utility_loss)
                                stats.append(get_stats(G))
                            #process and save data
                            row = []
                            row.append(n_nodes)
                            row.append(tie_utility_loss)
                            row.append(influencer_prop)
                            row.append(mean)
                            row.append(sd)
                            row.append(i)
                            for day in range(days):
                                row.append(stats[day]["tie_prop"])
                            data.append(row)

                            if (sim%100) == 0:
                                print("{0}% complete".format(round(100*sim/total_sims)))

        with open("records.csv", "w") as csvfile:
            writer = csv.writer(csvfile)
            for row in data:
                writer.writerow(row)

#Uncomment to run (80K+ simulations, long run time)
# run_sim([50, 100, 500],
#         10,
#         5,
#         [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
#         [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
#         [1, 2, 4, 8, 16, 32, 64],
#         [1, 2, 4, 8, 16, 32, 64])

#Small single simulation with visual output
G = nx.Graph()
tie_utility_loss = 0.7
influencer_prop = 0.3
make_nodes(G, 25)
normal_rand_edges(G, mean=2, sd=2)
influencer_id = add_influencer(G, influencer_prop)
stats = []
pos = nx.spring_layout(G)
switch_status = def_assess_changes(G, tie_utility_loss)

for day in range(10):
    #Make change based on previous day
    switch(G, switch_status)
    DAY = day+1
    if DAY == 3:
        #change tie pref
        G.nodes[influencer_id]["tie"] = 0
    #assess day
    switch_status = def_assess_changes(G, tie_utility_loss)
    stats.append(get_stats(G))

    draw(G, pos, DAY)

for i in stats:
    print(i["tie_prop"])
