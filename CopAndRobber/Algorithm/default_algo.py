import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

import sqlite3
import json

'''
Move to the shortest distance to robber.
@author KMY
@version 1.0
'''

engine = sqlite3.connect('./db.sqlite3')
node_df = pd.read_sql('SELECT * FROM node_information', engine, index_col='nodeId')
node_df['linkedNode'] = node_df['linkedNode'].apply(lambda x : json.loads(x)) # json to list

def MoveNode(cops_cur_node, rob_cur_node):
    G = nx.Graph()
    G.add_nodes_from(node_df.index)

    for start_node in node_df.index:
        for end_node in node_df.loc[start_node, 'linkedNode']:
            G.add_edge(start_node, end_node)

    next_cop_nodes = []
    for cop_cur_node in cops_cur_node:
        next_cop_nodes.append(nx.shortest_path(G, source=cop_cur_node, target=rob_cur_node)[1])
    
    return cops_cur_node, next_cop_nodes