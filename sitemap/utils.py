import pandas as pd
import sqlite3
import json

# read node data from database
def readNodesFromDB():
    engine = sqlite3.connect('./db.sqlite3')
    node_df = pd.read_sql('SELECT * FROM node_information', engine, index_col='nodeId')
    node_df['linkedNode'] = node_df['linkedNode'].apply(lambda x : json.loads(x)) # json to list

    return node_df

# randomize cop and robber's start node
def randomStartNode(node_df, cop_num):
    random_nodes = node_df.sample(cop_num+1).index.tolist()
    cop_random_nodes = random_nodes[:cop_num]
    rob_random_node = random_nodes[-1]

    return cop_random_nodes, rob_random_node