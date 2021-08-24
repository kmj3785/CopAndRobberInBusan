import sys
import pandas as pd
import networkx as nx
import math
import queue
import copy
from itertools import combinations

# 기존 형식과 유사하게 Node class 정의
class Node:
    def __init__(self, linkedNode):
        self.linkedNode = linkedNode

class CopNextNodes:
    def __init__(self, _distance=0, _nextNode=[]):
        self.distance = _distance
        self.nextNode = copy.deepcopy(_nextNode)

def BFS(currentID, endID, node_df, visited=[], path=[]):
    path.append(currentID)

    if currentID == endID:
        return path
    
    for nextID in node_df.loc[currentID, 'linkedNode']:
        if nextID not in visited:
            visited.append(nextID)
            BFS(nextID, endID, node_df, visited, path)


def BFS_next_nodes(startID, endID, node_df):
    costs = {}
    parents = {}

    currentID = startID
    q = queue.Queue()
    q.put(currentID)
    costs[currentID] = 0

    while not q.empty():
        currentID = q.get()

        for nextID in node_df.loc[currentID, 'linkedNode']:
            if (nextID in costs and costs[nextID] >= costs[currentID] + 1) or nextID not in costs:
                costs[nextID] = costs[currentID] + 1
                if nextID not in parents:
                    parents[nextID] = []
                if currentID not in parents[nextID]:
                    parents[nextID].append(currentID)
                q.put(nextID)

    next_nodes = [endID]
    distance = 0

    if endID != startID:
        distance += 1

        while parents[next_nodes[0]][0] != startID:
            new_next_nodes = []
            for next_node in next_nodes:
                for parent_node in parents[next_node]:
                    if parent_node not in new_next_nodes:
                        new_next_nodes.append(parent_node)
            next_nodes = copy.deepcopy(new_next_nodes)
            distance += 1

    return CopNextNodes(distance, next_nodes)

def permutations(array, c):
    if len(array) >= c:
        return permutations_2(array, c)
    else:
        return permutations_3(array, c)

# 중복x  길이 c 수보다 많거나 같을 때
def permutations_2(array, c):
    for i in range(len(array)):
        if c == 1:
            yield [array[i]]
        else:
            for next in permutations_2(array[:i]+array[i+1:], c-1):
                yield [array[i]] + next

# 중복o 길이 c 수보다 작을 때
def permutations_3(array, c, turn = 0, number_of_dest=[], cop_goal_array=[]):
    if turn > c - 1:
        yield cop_goal_array
        return
        
    if turn == 0:
        number_of_dest = [0 for i in range(len(array))]
        cop_goal_array = [0 for i in range(c)]

    for dest in range(0, len(array)):

        copy_number_of_dest = number_of_dest.copy()
        copy_cop_goal_array = cop_goal_array.copy()

        if copy_number_of_dest[dest] < c // len(array) + 1:
            copy_cop_goal_array[turn] = dest
            copy_number_of_dest[dest] += 1
            for next in permutations_3(array, c, turn+1, copy_number_of_dest, copy_cop_goal_array):
                yield next

# new cur cop node에서 rob node까지의 벡터 합이 0에 가까우면 True 반환
def sum_vector_power(new_cop_nodes, old_cop_nodes, rob_node, node_df):
    new_cop_vector_sum = 0
    old_cop_vector_sum = 0
    for cop in new_cop_nodes:
        new_cop_vector_sum += math.cos(math.atan2(node_df.loc[rob_node, 'longitude'] - node_df.loc[cop, 'longitude'], node_df.loc[rob_node, 'latitude'] - node_df.loc[cop, 'latitude']))
    for cop in old_cop_nodes:
        old_cop_vector_sum += math.cos(math.atan2(node_df.loc[rob_node, 'longitude'] - node_df.loc[cop, 'longitude'], node_df.loc[rob_node, 'latitude'] - node_df.loc[cop, 'latitude']))

    if abs(new_cop_vector_sum) < abs(old_cop_vector_sum):
        return True
    else:
        return False

# 다음 node가 rob 위치인지 판별
def cal_next_cop_node(next_node=None, next_cop_node=None, cur_rob_node=None, distance = 0):
    if next_node == cur_rob_node or next_cop_node == cur_rob_node or distance == 0:
        return cur_rob_node
    else:
        return next_node

def MoveNode(cur_cop_nodes, cur_rob_node, node_df):
    cops_next = []

    for i, cop_node in enumerate(cur_cop_nodes):
        cops_next.append([])
        for linkedNode in node_df.loc[cur_rob_node, 'linkedNode']:
            cops_next[i].append(BFS_next_nodes(cop_node, linkedNode, node_df))

    next_cop_nodes = copy.deepcopy(cur_cop_nodes)
    min_weight = 10000000

    for index in permutations(list(range(0, len(node_df.loc[cur_rob_node, 'linkedNode']))), len(cur_cop_nodes)):
        weight = 0
        for i in range(0, len(cur_cop_nodes)):
            weight += cops_next[i][index[i]].distance
        
        temp_next_cop_nodes = []
        for i in range(0, len(cur_cop_nodes)):
            temp_next_cop_nodes.append(cal_next_cop_node(cops_next[i][index[i]].nextNode[0], next_cop_nodes[i], cur_rob_node, cops_next[i][index[i]].distance))
        
        if weight < min_weight:
            min_weight = weight
            next_cop_nodes = copy.deepcopy(temp_next_cop_nodes)

        elif weight == min_weight and sum_vector_power(temp_next_cop_nodes, next_cop_nodes, cur_rob_node, node_df):
            next_cop_nodes = copy.deepcopy(temp_next_cop_nodes)

    return next_cop_nodes