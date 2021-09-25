import os, sys

from networkx.generators.geometric import thresholded_random_geometric_graph
sys.path.append(os.getcwd())

import zipfile
import json
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np

from rnn.predict import predict
from CopAndRobber.Algorithm import default_algo, algo, rnn_algo, rob_algo
from rnn.utils import nodeId_to_group

'''
Compare the basic group experimental group (algo, rnn) with an average value, a maximum value, and a mode value.
It's data format is zip
@author KMY
@version 1.1, Change the output to side-by-side chart method.
'''

default_data_path = "./test/test_results/turn_default"
algorithm_data_path = "./test/test_results/turn_algorithm"
AI_data_path = "./test/test_results/turn_AI"

category = ['default', 'algorithm', 'AI']


# Select an algorithm type to generate data on the number of turns until the end.
def playGame(cop_start_nodes, rob_start_nodes, category_value):

    cop_num = len(cop_start_nodes[0])
    game_num = len(cop_start_nodes)
    threshold = 100
    all_turn = []

    for i in range(0, game_num):

        # initialize variable
        turn = 0
        past_cop_nodes = [0] * cop_num
        cur_cop_nodes = cop_start_nodes[i]
        cur_rob_node = rob_start_nodes[i]
        rob_path = [cur_rob_node]
        is_rob_turn = True

        temp_predict_rob_path = []
        temp_real_rob_path = []

        # calculate path
        while (cur_rob_node not in cur_cop_nodes) and turn < threshold:
            if is_rob_turn:
                cur_rob_node = rob_algo.MoveNode(cur_cop_nodes, cur_rob_node)
                rob_path.append(cur_rob_node)

                if category_value == 3:
                    group = nodeId_to_group(cur_rob_node)
                    temp_real_rob_path.append(group)

                is_rob_turn = False
            else:
                if category_value == 1:
                    past_cop_nodes, cur_cop_nodes = default_algo.MoveNode(cur_cop_nodes, cur_rob_node)
                elif category_value == 2:
                    past_cop_nodes, cur_cop_nodes = algo.MoveNode(cur_cop_nodes, cur_rob_node, past_cop_nodes)
                elif category_value == 3:
                    predict_rob_group = predict(rob_path)
                    past_cop_nodes, cur_cop_nodes = rnn_algo.MoveNode(cur_cop_nodes, cur_rob_node, past_cop_nodes, predict_rob_group)
                    temp_predict_rob_path.append(predict_rob_group)

                is_rob_turn = True
                turn += 1

        if (i+1)%(game_num*0.2) == 0:
                print(f'cop_num: {cop_num}, game_num: {game_num}, {i+1}번째까지의 데이터가 생성되었습니다.')

        all_turn.append(turn)

    if category_value == 1:
        with open(f'{default_data_path}_{cop_num:0>2}_{game_num:0>5}.json', "w") as json_file:
            json.dump(all_turn, json_file)
    elif category_value == 2:
        with open(f'{algorithm_data_path}_{cop_num:0>2}_{game_num:0>5}.json', "w") as json_file:
            json.dump(all_turn, json_file)
    elif category_value == 3:
        with open(f'{AI_data_path}_{cop_num:0>2}_{game_num:0>5}.json', "w") as json_file:
            json.dump(all_turn, json_file)

    print(f'cop_num: {cop_num}, game_num: {game_num}, 데이터 생성이 완료되었습니다.\n')

def generateData():
    category_value = int(input("\n어떤 알고리즘을 활용하여 데이터를 생성하시겠습니까?\n1.default\n2.algorithm\n3.AI\n"))

    start_nodes_zip = zipfile.ZipFile('./test/data/start_nodes.zip')
    file_list = zipfile.ZipFile.namelist(start_nodes_zip)

    for cop_file in file_list[:int(len(file_list)/2)]:
        print(cop_file)
        cop_start_nodes = json.load(start_nodes_zip.open(cop_file))
        cop_num = len(cop_start_nodes[0])
        game_num = len(cop_start_nodes)
        rob_start_nodes = json.load(start_nodes_zip.open(f'rob_start_nodes_{cop_num:0>2}_{game_num:0>5}.json'))
        playGame(cop_start_nodes, rob_start_nodes, category_value)

# Output various comparison values on the side-by-side chart.
def print_data():

    return
    
    # with open(default_data_path, "r") as json_file:
    #     default_data = json.load(json_file)
    # with open(algorithm_data_path, "r") as json_file:
    #     algorithm_data = json.load(json_file)
    # with open(AI_data_path, "r") as json_file:
    #     AI_data = json.load(json_file)

    # labels = ['Average', 'Max', 'Mode']
    # default_means   = [sum(default_data)/n_data,    max(default_data),  Counter(default_data).most_common(n=1)[0][0]]
    # algorithm_means = [sum(algorithm_data)/n_data,  max(algorithm_data),Counter(algorithm_data).most_common(n=1)[0][0]]
    # AI_means        = [sum(AI_data)/n_data,         max(AI_data),       Counter(AI_data).most_common(n=1)[0][0]]

    # x = np.arange(len(labels))   # the label locations
    # width = 0.2     # the width of the bars

    # fig, ax = plt.subplots()
    # rects1 = ax.bar(x - width,  default_means,   width, label='Default',    color = '#6481f5')
    # rects2 = ax.bar(x,          algorithm_means, width, label='Algorithm',  color = '#f56464')
    # rects3 = ax.bar(x + width,  AI_means ,       width, label='RNN',         color = '#ae65fc')

    # # Add some text for labels, title and custom x-axis tick labels, etc.
    # ax.set_ylabel('Number of turns')
    # ax.set_title('Number of turns by algorithm type', fontsize = 20)
    # ax.set_xticks(x)
    # ax.set_xticklabels(labels)
    # ax.legend()

    # ax.bar_label(rects1, padding=5)
    # ax.bar_label(rects2, padding=5)
    # ax.bar_label(rects3, padding=5)

    # fig.tight_layout()

    # plt.show()

if __name__ == '__main__':
    input_value = int(input("\n하고자하는 동작을 선택해주세요.\n1.데이터 생성\n2.데이터 출력\n3.종료\n"))

    while(input_value != 3):
        if(input_value == 1):
            generateData()

        elif (input_value == 2):    
            print_data()

        input_value = int(input("\n하고자하는 동작을 선택해주세요.\n1.데이터 생성\n2.데이터 출력\n3.종료\n"))