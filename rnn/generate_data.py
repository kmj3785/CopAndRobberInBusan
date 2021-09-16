import os, sys
sys.path.append(os.getcwd())

import pandas as pd
import sqlite3
import json
import time

from CopAndRobber.Algorithm import algo2
from CopAndRobber.Algorithm import default_algo
from CopAndRobber.Algorithm import rob_algo

# read node data from database
def readNodesFromDB():
    engine = sqlite3.connect('./db.sqlite3')
    node_df = pd.read_sql('SELECT * FROM node_information', engine, index_col='nodeId')
    node_df['linkedNode'] = node_df['linkedNode'].apply(lambda x : json.loads(x)) # json to list

    return node_df

# randomize start node
def randomStartNode(node_df):
    random_nodes = node_df.sample(4).index
    random_cop_nodes = list(int(x) for x in random_nodes[0:3])
    random_rob_node = int(random_nodes[-1])

    return random_cop_nodes, random_rob_node

# check if game is finished
def isFinish(cops_cur_node, rob_cur_node):
    result = False
    for cop_cur_node in cops_cur_node:
        if cop_cur_node == rob_cur_node:
            result = True
    return result

node_df = readNodesFromDB()

rob_paths_df = pd.DataFrame(columns=['turn', 'path', 'copAlgorithm'])

# input data size and cop algorithm
learning_data_size = int(input("데이터를 얼마나 생성하시겠습니까?: "))
cop_algorithm = int(input("경찰의 알고리즘을 선택하세요.\n1.algo2\n2.default\n"))

start_time = time.time()

# generate learning data by learning_data_size
for i in range(0, learning_data_size):
    # init game variable
    turn = 1
    is_rob_turn = True
    cops_cur_node, rob_cur_node = randomStartNode(node_df)

    # play game until robber is caught by cops
    rob_nodes = [rob_cur_node]
    while isFinish(cops_cur_node, rob_cur_node)!=True:
        if is_rob_turn:
            turn += 1
            rob_cur_node = rob_algo.MoveNode(cops_cur_node, rob_cur_node, node_df)
            rob_nodes.append(rob_cur_node)
        else:
            if cop_algorithm == 1:
                cops_cur_node = algo2.MoveNode(cops_cur_node, rob_cur_node, node_df)
            else:
                cops_cur_node = default_algo.MoveNode(cops_cur_node, rob_cur_node, node_df)
        is_rob_turn = not is_rob_turn
    
    # add robber path to dataframe
    rob_nodes_df = pd.DataFrame([[len(rob_nodes), json.dumps(rob_nodes), 'algo2']], columns=['turn', 'path', 'copAlgorithm'])
    rob_paths_df = rob_paths_df.append(rob_nodes_df)
    rob_paths_df = rob_paths_df.reset_index(drop=True)

end_time = time.time()-start_time

print('데이터의 생성이 완료되었습니다.')
print(f'데이터 생성에 걸린 시간: {end_time}s')

# save to database
save_to_database = input("데이터베이스에 저장할까요?(y/n): ")
if save_to_database == 'y':
    engine = sqlite3.connect("./db.sqlite3")
    rob_paths_df.to_sql(name='rob_paths', con=engine, if_exists='append', index=False)
    print('데이터베이스에 저장 완료했습니다.')
