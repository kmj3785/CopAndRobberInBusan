import os, sys
sys.path.append(os.getcwd())
import json

from sitemap.utils import readNodesFromDB, randomStartNode

if __name__ == '__main__':
    node_df = readNodesFromDB()

    generate_nums = [int(x) for x in input('데이터를 얼마나 생산하겠습니까?(리스트) : ').split()]
    cop_min, cop_max = map(int, input('경찰 수의 최소와 최대를 입력하세요 : ').split())

    for cop_num in range(cop_min, cop_max+1):
        for generate_num in generate_nums:            
            cop_start_nodes = []
            rob_start_nodes = []

            for i in range(0, generate_num):
                cop_node, rob_node = randomStartNode(node_df, cop_num)
                cop_start_nodes.append(cop_node)
                rob_start_nodes.append(rob_node)

            with open(f'./test/data/cop_start_nodes_{cop_num:0>2}_{generate_num:0>5}.json', 'w') as outfile:
                json.dump(cop_start_nodes, outfile, indent=4)
            with open(f'./test/data/rob_start_nodes_{cop_num:0>2}_{generate_num:0>5}.json', 'w') as outfile:
                json.dump(rob_start_nodes, outfile, indent=4)