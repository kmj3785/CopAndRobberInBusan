import sys
import queue
import copy
import pandas as pd
import networkx as nx
from itertools import product

import sqlite3
import json


engine = sqlite3.connect('./db.sqlite3')
node_df = pd.read_sql('SELECT * FROM node_information', engine, index_col='nodeId')
node_df['linkedNode'] = node_df['linkedNode'].apply(lambda x : json.loads(x)) # json to list

# cop의 다음 경로 정보(도착 지점 전 ID, 다음 node ID, 거리)
class NextRobNode:
    def __init__(self, nodeID, minDistance, totalDistance):
        self.nodeID = nodeID
        self.minDistance = minDistance
        self.totalDistance = totalDistance

def CalDistance(startID, endID):
    if startID == endID:
        return 0

    costs = {}
    parents = {}

    currentID = startID
    q = queue.Queue()
    q.put(currentID)
    costs[currentID] = 1

    while not q.empty():
        currentID = q.get()

        for nextID in node_df.loc[currentID, 'linkedNode']:
            if (nextID in costs and costs[nextID] >= costs[currentID] + 1) or nextID not in costs:
                costs[nextID] = costs[currentID] + 1
                parents[nextID] = currentID
                if nextID == endID:
                    q.queue.clear()
                else:
                    q.put(nextID)
        
    return costs[endID]

def CalNextRobNode(next_rob_node, cur_cop_nodes):
    distances = []
    for cur_cop_node in cur_cop_nodes:
        distances.append(CalDistance(next_rob_node, cur_cop_node))
    return NextRobNode(next_rob_node, min(distances), sum(distances))

def MoveNode(cur_cop_nodes, cur_rob_node):
    next_rob_nodes = []
    next_rob_node = NextRobNode(cur_rob_node, 0, 0)

    for rob_node in node_df.loc[cur_rob_node, 'linkedNode']:
        next_rob_nodes.append(CalNextRobNode(rob_node, cur_cop_nodes))
        if next_rob_node.minDistance < next_rob_nodes[-1].minDistance:
            next_rob_node = next_rob_nodes[-1]
        elif next_rob_node.minDistance == next_rob_nodes[-1].minDistance and next_rob_node.totalDistance < next_rob_nodes[-1].totalDistance:
            next_rob_node = next_rob_nodes[-1]

    return next_rob_node.nodeID