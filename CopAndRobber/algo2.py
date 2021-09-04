import sys
import queue
import copy
import pandas as pd
import networkx as nx
from itertools import product

# cop의 다음 경로 정보(도착 지점 전 ID, 다음 node ID, 거리)
class Path:
    def __init__(self, robLinkedNodeID, nextNodeID, distance):
        self.robLinkedNodeID = robLinkedNodeID
        self.nextNodeID = nextNodeID
        self.distance = distance

def CalPath(startID, endID, copID, node_df):
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
        
    return Path(parents[endID], startID, costs[endID])

def MoveNode(cur_cop_nodes, cur_rob_node, node_df):
    # robber linekd Node ID를 key로, r각 
    paths_to_rob = []

    for index, cop_node in enumerate(cur_cop_nodes):
        paths_to_rob.append([])

        if cop_node == cur_rob_node:
            paths_to_rob[index].append(Path(None, cur_rob_node, 0))
            continue

        for cop_linked_node in node_df.loc[cop_node, 'linkedNode']:
            cop_path = CalPath(cop_linked_node, cur_rob_node, cop_node, node_df)

            # 현재 linked node로 rob에게 도달할 수 없을 시
            if cop_path == None:
                continue
            
            paths_to_rob[index].append(cop_path)

    next_cop_nodes = copy.deepcopy(cur_cop_nodes)
    reachable_node_num = 0 # 도달 가능한 rob의 linked Node 수
    total_distance = sys.maxsize

    for path_to_rob in product(*paths_to_rob):
        temp_reachable_nodes = []
        temp_total_distance = 0
        
        for cop_path in path_to_rob:
            if cop_path.robLinkedNodeID not in temp_reachable_nodes:
                temp_reachable_nodes.append(cop_path.robLinkedNodeID)
            temp_total_distance += cop_path.distance
        
        if (len(temp_reachable_nodes) > reachable_node_num) or (len(temp_reachable_nodes) == reachable_node_num and temp_total_distance < total_distance):
            reachable_node_num = len(temp_reachable_nodes)
            total_distance = temp_total_distance
            next_cop_nodes = []
            for cop_path in path_to_rob:
                next_cop_nodes.append(cop_path.nextNodeID)

    return next_cop_nodes