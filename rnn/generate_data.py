import os, sys
sys.path.append(os.getcwd())

import pandas as pd
import sqlite3
import json
import time
import copy

from CopAndRobber.Algorithm import algo2, default_algo, rob_algo

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

rob_paths_df = pd.DataFrame(columns=['timestamp', 'turn', 'path', 'copAlgorithm'])
cop_paths_df = pd.DataFrame(columns=['timestamp', 'turn', 'path', 'copAlgorithm'])

# input data size and cop algorithm
learning_data_size = int(input("데이터를 얼마나 생성하시겠습니까?: "))
saving_data_size = int(input("데이터를 몇 번마다 저장할까요?: "))
cop_algorithm = int(input("경찰의 알고리즘을 선택하세요.\n1.algo2\n2.default\n"))
cop_algorithm_txt = 'default'

start_time = time.time()

# generate learning data by learning_data_size
for i in range(0, learning_data_size):
    # init game variable
    turn = 1
    is_rob_turn = True
    cops_cur_node, rob_cur_node = randomStartNode(node_df)
    cops_past_node = [0, 0, 0]

    # current game number
    if (i+1)%(round(learning_data_size*0.1)) == 0:
        print(f'Current game is {i+1}th')

    # save to DB every 5000 turn
    if (i+1)%saving_data_size == 0:
        engine = sqlite3.connect("./db.sqlite3")
        rob_paths_df.to_sql(name='rob_paths', con=engine, if_exists='append', index=False)
        cop_paths_df.to_sql(name='cop_paths', con=engine, if_exists='append', index=False)
        rob_paths_df = pd.DataFrame(columns=['timestamp', 'turn', 'path', 'copAlgorithm'])
        cop_paths_df = pd.DataFrame(columns=['timestamp', 'turn', 'path', 'copAlgorithm'])
        print(f'{i+1}번째까지 데이터베이스에 저장 완료했습니다.')

    # play game until robber is caught by cops
    rob_nodes = [rob_cur_node]
    cop_nodes = [cops_cur_node]
    while isFinish(cops_cur_node, rob_cur_node)!=True:
        # check game turn and end game if game turn is over 100
        if turn >= 100:
            print('Current game turn is over 200. End game by force')
            break

        if is_rob_turn:
            turn += 1
            rob_cur_node = rob_algo.MoveNode(cops_cur_node, rob_cur_node)
            rob_nodes.append(rob_cur_node)
        else:
            if cop_algorithm == 1:
                cop_algorithm_txt = 'algo2'
                cops_past_node, cops_cur_node = algo2.MoveNode(cops_cur_node, rob_cur_node, cops_past_node)
            elif cop_algorithm == 2:
                cop_algorithm_txt = 'default'
                cops_cur_node = default_algo.MoveNode(cops_cur_node, rob_cur_node, node_df)
            cop_nodes.append(cops_cur_node)
        is_rob_turn = not is_rob_turn
    
    timestamp = pd.Timestamp.now()
    # add robber path to dataframe
    rob_nodes_df = pd.DataFrame([[timestamp, turn, json.dumps(rob_nodes), cop_algorithm]], columns=['timestamp', 'turn', 'path', 'copAlgorithm'])
    rob_paths_df = rob_paths_df.append(rob_nodes_df, ignore_index=True)

    # add cop path to dataframe
    cop_nodes_df = pd.DataFrame([[timestamp, turn, json.dumps(cop_nodes), cop_algorithm]], columns=['timestamp', 'turn', 'path', 'copAlgorithm'])
    cop_paths_df = cop_paths_df.append(cop_nodes_df, ignore_index=True)

end_time = time.time()-start_time

print('데이터의 생성이 완료되었습니다.')
print(f'데이터 생성에 걸린 시간: {end_time}s')

# save to database
# save_to_database = input("데이터베이스에 저장할까요?(y/n): ")
# if save_to_database == 'y':
engine = sqlite3.connect("./db.sqlite3")
rob_paths_df.to_sql(name='rob_paths', con=engine, if_exists='append', index=False)
cop_paths_df.to_sql(name='cop_paths', con=engine, if_exists='append', index=False)
print('데이터베이스에 저장 완료했습니다.')
