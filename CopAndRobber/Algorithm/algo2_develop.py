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

G = nx.Graph()
G.add_nodes_from(node_df.index)

for start_node in node_df.index:
    for end_node in node_df.loc[start_node, 'linkedNode']:
        G.add_edge(start_node, end_node)


# cop의 다음 경로 정보(도착 지점 전 ID, 다음 node ID, 거리)
class Path:
    def __init__(self, targetNodeID, nextNodeID, distance):
        self.targetNodeID = targetNodeID
        self.nextNodeID = nextNodeID
        self.distance = distance

def differList(list1, list2):
    returnValue = True

    for i in range(0, len(list1)):
        if list1[i] == list2[i]:
            returnValue = False
            break

    return returnValue

# 시작 노드, 끝 노드, cop이 있는 node 입력
# isNear일 시, return: Path(목표로 하는 endID의 linkedNode, 시작 node, 거리)
# isNear이 아닐 시,    Path(목표로 하는 endID, 시작 node, 거리)
def CalToPath(startID, endID, copID, isNear):
    if startID == endID:
        return Path(endID, endID, 1)

    costs = {}
    parents = {}

    currentID = startID
    q = queue.Queue()
    q.put(currentID)
    costs[currentID] = 1

    while not q.empty():
        currentID = q.get()

        for nextID in node_df.loc[currentID, 'linkedNode']:
            if nextID != copID and ((nextID in costs and costs[nextID] >= costs[currentID] + 1) or nextID not in costs):
                costs[nextID] = costs[currentID] + 1
                parents[nextID] = currentID
                if nextID == endID:
                    q.queue.clear()
                else:
                    q.put(nextID)

    # 현재 linkedNode로 rob까지 도달할 수 없을 시
    if endID not in parents:
        return None
        
    if isNear:
        return Path(parents[endID], startID, costs[endID])
    else:
        return Path(endID, startID, costs[endID])

def MoveNode(cur_cop_nodes, cur_rob_node, past_cop_nodes, predict_rob_next_group):
    # 예측한 rob의 다음 그룹 node들 정의
    rob_next_group_nodes = node_df[node_df.groupNum == 14]
    rob_next_group_nodes = rob_next_group_nodes[rob_next_group_nodes.isCorner == False].index

    # robber linekd Node ID를 key로, r각 
    paths_to_rob = []

    for index, cop_node in enumerate(cur_cop_nodes):
        paths_to_rob.append([])

        if cop_node == cur_rob_node:
            paths_to_rob[index].append(Path(None, cur_rob_node, 0))
            continue

        if (nx.shortest_path_length(G, cop_node, cur_rob_node) < 10) or node_df.loc[cop_node, 'groupNum'] == predict_rob_next_group:
            for cop_linked_node in node_df.loc[cop_node, 'linkedNode']:
                cop_path = CalToPath(cop_linked_node, cur_rob_node, cop_node, True)

                # 현재 linked node로 rob까지 도달할 수 있을 시
                if cop_path != None:
                    paths_to_rob[index].append(cop_path)
        
        else:
            for group_node in rob_next_group_nodes:
                for cop_linked_node in node_df.loc[cop_node, 'linkedNode']:
                    cop_path = CalToPath(cop_linked_node, group_node, cop_node, False)

                    # 현재 linked node로 group node까지 도달할 수 있을 시
                    if cop_path != None:
                        paths_to_rob[index].append(cop_path)
            

    next_cop_nodes = copy.deepcopy(cur_cop_nodes)
    reachable_node_num = 0 # 도달 가능한 rob의 linked Node 수
    next_cop_node_num = 0 # 서로 다른 cop node 수
    total_distance = sys.maxsize

    for path_to_rob in product(*paths_to_rob):
        temp_reachable_nodes = []
        temp_total_distance = 0
        temp_next_nodes = []
        
        for cop_path in path_to_rob:
            if cop_path.targetNodeID not in temp_reachable_nodes:
                temp_reachable_nodes.append(cop_path.targetNodeID)
            temp_total_distance += cop_path.distance
            if cop_path.nextNodeID not in temp_next_nodes:
                temp_next_nodes.append(cop_path.nextNodeID)
        
        if len(temp_next_nodes) >= next_cop_node_num and differList(temp_next_nodes, past_cop_nodes) and ((len(temp_reachable_nodes) > reachable_node_num)
            or (len(temp_reachable_nodes) == reachable_node_num and temp_total_distance < total_distance)):
            reachable_node_num = len(temp_reachable_nodes)
            total_distance = temp_total_distance
            next_cop_node_num = len(temp_next_nodes)
            next_cop_nodes = []
            for cop_path in path_to_rob:
                next_cop_nodes.append(cop_path.nextNodeID)

        temp_next_nodes.clear()
        temp_reachable_nodes.clear()

    return cur_cop_nodes, next_cop_nodes

if __name__ == '__main__':
    print(MoveNode([1400010600, 1400005600, 1400003300], 1400002900, [0, 0, 0], 28))