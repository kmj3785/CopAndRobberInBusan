import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

def MoveNode(cops_cur_node, rob_cur_node, node_df):
    G = nx.Graph()
    G.add_nodes_from(node_df.index)

    for start_node in node_df.index:
        for end_node in node_df.loc[start_node, 'linkedNode']:
            G.add_edge(start_node, end_node)

    next_cop_nodes = []
    for cop_cur_node in cops_cur_node:
        next_cop_nodes.append(nx.shortest_path(G, source=cop_cur_node, target=rob_cur_node)[1])
    
    return next_cop_nodes