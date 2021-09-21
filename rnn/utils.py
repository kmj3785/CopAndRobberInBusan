import torch
import sqlite3
import json
import pandas as pd

N_GROUP = 34

engine = sqlite3.connect('./db.sqlite3')
node_df = pd.read_sql('SELECT * FROM node_information', engine, index_col='nodeId')
path_df = pd.read_sql('SELECT * FROM rob_paths', engine)
path_df['path'] = path_df['path'].apply(lambda x : json.loads(x)) # json to list

def nodeId_to_group(nodeId):
    groupNum = node_df.loc[nodeId, 'groupNum']
    return groupNum

# Return the tensor from groupNum which nodeId belongs.
def nodeId_to_tensor(nodeId):
    tensor = torch.zeros(1, N_GROUP)
    tensor[0][nodeId_to_group(nodeId)-1] = 1
    return tensor

# group -> tensor
def group_to_tensor(index):
    tensor = torch.zeros(1, N_GROUP)
    tensor[0][index-1] = 1
    return tensor

# read a data, one hot encoding
def path_to_tensor(path):
    one_hot_tensor = torch.zeros(len(path), 1, N_GROUP)
    tensor = torch.zeros(len(path), 1, dtype=torch.long)
    for i, nodeId in enumerate(path):
        one_hot_tensor[i][0][nodeId_to_group(nodeId)-1] = 1
        tensor[i][0] = nodeId_to_group(nodeId)-1
    return one_hot_tensor, tensor

def create_path_tensor():
    for i in range(0, len(path_df)):
        yield path_to_tensor(path_df.loc[i, 'path'])