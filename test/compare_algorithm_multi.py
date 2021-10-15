import os, sys

from networkx.generators.geometric import thresholded_random_geometric_graph
from networkx.generators.social import les_miserables_graph
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

# default_data_path = "./test/test_results/turn_default"
# algorithm_data_path = "./test/test_results/turn_algorithm"
# AI_data_path = "./test/test_results/turn_AI"

algorithms = ['dijkstra', 'rabbit-herding', 'RNN']
turn_data_paths = ["./test/test_results/turn_default", "./test/test_results/turn_algorithm", "./test/test_results/turn_AI"]


# Select an algorithm type to generate data on the number of turns until the end.
def playGame(cop_start_nodes, rob_start_nodes, algorithm_value):

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

                if algorithm_value == 3:
                    group = nodeId_to_group(cur_rob_node)
                    temp_real_rob_path.append(group)

                is_rob_turn = False
            else:
                if algorithm_value == 1:
                    past_cop_nodes, cur_cop_nodes = default_algo.MoveNode(cur_cop_nodes, cur_rob_node)
                elif algorithm_value == 2:
                    past_cop_nodes, cur_cop_nodes = algo.MoveNode(cur_cop_nodes, cur_rob_node, past_cop_nodes)
                elif algorithm_value == 3:
                    predict_rob_group = predict(rob_path)
                    past_cop_nodes, cur_cop_nodes = rnn_algo.MoveNode(cur_cop_nodes, cur_rob_node, past_cop_nodes, predict_rob_group)
                    temp_predict_rob_path.append(predict_rob_group)

                is_rob_turn = True
                turn += 1

        if (i+1)%(game_num*0.2) == 0:
                print(f'cop_num: {cop_num}, game_num: {game_num}, {i+1}번째까지의 데이터가 생성되었습니다.')

        all_turn.append(turn)

    with open(f'{turn_data_paths[algorithm_value-1]}_{cop_num:0>2}_{game_num:0>5}.json', "w") as json_file:
            json.dump(all_turn, json_file)

    print(f'cop_num: {cop_num}, game_num: {game_num}, 데이터 생성이 완료되었습니다.\n')

def generateData():
    algorithm_value = int(input("\n어떤 알고리즘을 활용하여 데이터를 생성하시겠습니까?\n1.default\n2.algorithm\n3.AI\n"))

    start_nodes_zip = zipfile.ZipFile('./test/data/start_nodes.zip')
    file_list = zipfile.ZipFile.namelist(start_nodes_zip)

    for cop_file in file_list[:int(len(file_list)/2)]:
        print(cop_file)
        cop_start_nodes = json.load(start_nodes_zip.open(cop_file))
        cop_num = len(cop_start_nodes[0])
        game_num = len(cop_start_nodes)
        rob_start_nodes = json.load(start_nodes_zip.open(f'rob_start_nodes_{cop_num:0>2}_{game_num:0>5}.json'))
        playGame(cop_start_nodes, rob_start_nodes, algorithm_value)

def read_data(cop_num, game_num):
    turn_datas = {}
    for i in range(len(turn_data_paths)):
        with open(f'{turn_data_paths[i]}_{cop_num:0>2}_{game_num:0>5}.json', 'r') as json_file:
            turn_datas[algorithms[i]] = json.load(json_file)

    return turn_datas

# Print average or worst graph by number of cops. Type indicates average or worst
def printCopCaseGraph(cop_nums, game_nums, colors, type):
    for game_num in game_nums:
        avg_turn_datas = {}
        for algorithm in algorithms:
            avg_turn_datas[algorithm] = []
        for cop_num in cop_nums:

            turn_datas = read_data(cop_num, game_num)

            ratio = 1 if type=='average' else 0.1
            for algorithm, turn_data in turn_datas.items():
                turn_data.sort(reverse=True)
                avg_turn_datas[algorithm].append(sum(turn_data[:int(len(turn_data)*ratio)])/int(len(turn_data)*ratio))
        for algorithm in algorithms:
            plt.plot(cop_nums, avg_turn_datas[algorithm], label=algorithm, color=colors[algorithm])

        ylimit = 20 if type=='average' else 70

        plt.ylim(0, ylimit)
        plt.xlabel('Number of Cops')
        plt.ylabel(f'{type.capitalize()} Case')
        plt.title(f'{type.capitalize()} Case by Cop Number : n(Game)={game_num}')
        plt.legend()
        plt.grid(True, alpha=0.5)
        plt.savefig(f'./test/charts/{type}_cop_case_{game_num:0>5}.jpg')
        plt.clf()

# Print total graph(average, worst, best) by number of cops
def printCopCaseTotalGraph(cop_nums, game_num):
    avg_turn_datas = {}
    for algorithm in algorithms:
        avg_turn_datas[algorithm] = {'average': [], 'worst':[], 'best': []}
    for cop_num in cop_nums:

        turn_datas = read_data(cop_num, game_num)

        ratio = 0.1
        for algorithm, turn_data in turn_datas.items():
            avg_turn_datas[algorithm]['average'].append(sum(turn_data)/len(turn_data))

            turn_data.sort(reverse=True)
            avg_turn_datas[algorithm]['worst'].append(sum(turn_data[:int(len(turn_data)*ratio)])/int(len(turn_data)*ratio))
            
            turn_data.sort(reverse=False)
            avg_turn_datas[algorithm]['best'].append(sum(turn_data[:int(len(turn_data)*ratio)])/int(len(turn_data)*ratio))

    for algorithm in algorithms:
        plt.plot(cop_nums, avg_turn_datas[algorithm]['average'], label='Average Case', color='blue')
        plt.plot(cop_nums, avg_turn_datas[algorithm]['worst'], label='Worst Case', color='red')
        plt.plot(cop_nums, avg_turn_datas[algorithm]['best'], label='Best Case', color='green')

        ylimit = 70
        plt.ylim(0, ylimit)
        plt.xlabel('Number of Cops')
        plt.ylabel('Average Case')
        plt.title(f'Average, Worst, Best Case : {algorithm}, n(Game)={game_num}')
        plt.legend()
        plt.grid(True, alpha=0.5)
        plt.savefig(f'./test/charts/wab_cop_case_{algorithm}_{game_num:0>5}.jpg')
        plt.clf()


# Print histogram of number of turns.
def printTurnCaseGraph(cop_nums, game_nums, colors):
    for game_num in game_nums:
        for cop_num in cop_nums:
            turn_datas = read_data(cop_num, game_num)

            xlimit = 100
            if game_num <= 1000:
                ylimit = 300
            elif game_num <= 2000:
                ylimit = 600
            elif game_num <= 5000:
                ylimit = 1400
            else:
                ylimit = 2000
            
            for algorithm in algorithms:
                binwidth = 2
                n, bins = np.histogram(turn_datas[algorithm], bins=range(0, xlimit + binwidth, binwidth))
                bin_centers = 0.5 * (bins[1:] + bins[:-1])
                plt.plot(bin_centers, n, label=algorithm, color=colors[algorithm])

            plt.xlim(0, xlimit)
            plt.ylim(0, ylimit)
            plt.xlabel('Number of Turns')
            plt.ylabel('Number of Cases')
            plt.title('Game Result')
            plt.legend()
            plt.grid(True, alpha=0.5)
            plt.savefig(f'./test/charts/hist_turn_case_{cop_num:0>2}_{game_num:0>5}.jpg')
            plt.clf()

# Output various comparison values on the side-by-side chart.
def printData():

    print_type = int(input('\n출력할 그래프를 선택하세요: \n1.경찰수에 따른 잡힌 횟수 그래프\n2.잡힌 횟수 히스토그램\n'))

    cop_nums = [x for x in range(2, 11)]
    game_nums = [1000, 2000, 5000]
    algorithm_colors = {'dijkstra': 'green', 'rabbit-herding': 'blue', 'RNN': 'red'}

    if print_type == 1:
        graph_type = int(input('\n원하는 케이스를 선택하세요: \n1.Average\n2.Worst\n3.Average & Worst & Best\n'))
        
        if graph_type == 1:
            printCopCaseGraph(cop_nums, game_nums, algorithm_colors, 'average')
        elif graph_type == 2:
            printCopCaseGraph(cop_nums, game_nums, algorithm_colors, 'worst')
        else:
            game_num = 5000
            printCopCaseTotalGraph(cop_nums, game_num)

    else:
        printTurnCaseGraph(cop_nums, game_nums, algorithm_colors)

if __name__ == '__main__':
    input_value = int(input("\n하고자하는 동작을 선택해주세요.\n1.데이터 생성\n2.데이터 출력\n3.종료\n"))

    while(input_value != 3):
        if(input_value == 1):
            generateData()

        elif (input_value == 2):    
            printData()

        input_value = int(input("\n하고자하는 동작을 선택해주세요.\n1.데이터 생성\n2.데이터 출력\n3.종료\n"))