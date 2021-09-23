from django.shortcuts import render
from django.http import HttpResponse
import folium
from folium.features import DivIcon
from branca.element import Element

import json
from collections import OrderedDict

import pandas as pd
import sqlite3

from CopAndRobber.Algorithm import algo, default_algo, rnn_algo
from rnn import predict, utils

cop_num = 3

# default values
default_cops_cur_node = [1400002200, 1400002600, 1400003300] # ?, 금정구청, ?
default_cops_past_node = [0, 0, 0]
default_rob_cur_node = 1400002900 # 금정경찰서교차로
default_rob_path = []
default_turn = 1  
default_is_rob_turn = True

node_df = pd.DataFrame()

# map 구성
def initMap(is_rob_turn, rob_cur_node, cops_cur_node):
    global node_df

    # read node data from database
    engine = sqlite3.connect('./db.sqlite3')
    node_df = pd.read_sql('SELECT * FROM node_information', engine, index_col='nodeId')
    node_df['linkedNode'] = node_df['linkedNode'].apply(lambda x : json.loads(x)) # json to list

    # Create map, 지도 중심 금정구청으로 잡음
    m = folium.Map(location=[node_df.loc[rob_cur_node, 'latitude'], node_df.loc[rob_cur_node, 'longitude']], zoom_start=15)

    # draw graph on map
    for row_index, row in node_df.iterrows():
        enode_list = row['linkedNode']
        for enode in enode_list:
            fnode_point = [row['latitude'], row['longitude']]
            enode_point = [node_df.loc[enode, 'latitude'], node_df.loc[enode, 'longitude']]
            folium.PolyLine([fnode_point, enode_point]).add_to(m)

    # Show nodes that can be moved by a thief.
    if is_rob_turn:
        for i in range(0, len(node_df.loc[rob_cur_node, 'linkedNode'])):
            linked_node_id = node_df.loc[rob_cur_node, 'linkedNode'][i]
            folium.Marker([node_df.loc[linked_node_id, 'latitude'], node_df.loc[linked_node_id, 'longitude']],
                        icon=DivIcon(
                            icon_size=(150,36),
                            icon_anchor=(7,20),
                            html='<div style="background-color: white; width:25px; height:25px; border-radius:50%; text-align:center; line-height:25px; font-size:15px;">'
                                    +(i).__str__()+'</div>',
                        )).add_to(m)
    
    # Show Cop and Robber location
    folium.Marker([node_df.loc[rob_cur_node, 'latitude'], node_df.loc[rob_cur_node, 'longitude']], icon=folium.Icon(icon='car', prefix='fa', color = 'red')).add_to(m)
    for i in range(0, cop_num):
        folium.Marker([node_df.loc[cops_cur_node[i], 'latitude'], node_df.loc[cops_cur_node[i], 'longitude']], icon=folium.Icon(icon='star', color = 'blue')).add_to(m)

    # Get html representation of map
    m = m._repr_html_()
    return m


def map(request):
    turn = request.session.get('turn', default_turn)
    is_rob_turn = request.session.get('is_rob_turn', default_is_rob_turn)
    cops_cur_node = request.session.get('cops_cur_node', default_cops_cur_node)
    rob_cur_node = request.session.get('rob_cur_node', default_rob_cur_node)

    is_finish = False

    for i in range(0, cop_num):
        if cops_cur_node[i] == rob_cur_node:
            is_finish = True

    context = {
        'm': initMap(is_rob_turn, rob_cur_node, cops_cur_node),
        'turn' : turn,
        'is_rob_turn' : is_rob_turn,
        'linked_node_num' : len(node_df.loc[rob_cur_node, 'linkedNode']),
        'is_finish' : is_finish,
    }

    return render(request, 'sitemap/map.html', context)

# Change Cop/Robber location
def moveNextNode(request):
    turn = request.session.get('turn', default_turn)
    is_rob_turn = request.session.get('is_rob_turn', default_is_rob_turn)
    cops_cur_node = request.session.get('cops_cur_node', default_cops_cur_node)
    cops_past_node = request.session.get('cops_past_node', default_cops_past_node)
    rob_cur_node = request.session.get('rob_cur_node', default_rob_cur_node)
    rob_path = request.session.get('rob_path', default_rob_path)

    if is_rob_turn:
        request.session['turn'] = turn + 1
        request.session['rob_cur_node'] = node_df.loc[rob_cur_node, 'linkedNode'][int(request.POST['next_node'])]
        request.session['rob_path'].append(request.session['rob_cur_node'])
        request.session['is_rob_turn'] = False

    else:
        request.session['cops_past_node'], request.session['cops_cur_node'] = rnn_algo.MoveNode(cops_cur_node, rob_cur_node, cops_past_node, predict.predict(rob_path))
        # request.session['cops_cur_node'] = default_algo.MoveNode(cops_cur_node, rob_cur_node, node_df)
        request.session['is_rob_turn'] = True

    return render(request, 'sitemap/map.html')

# randomize cop and robber's start node
def randomStartNode(request):
    random_nodes = node_df.sample(4).index
    request.session['cops_cur_node'] = list(int(x) for x in random_nodes[0:3])
    request.session['cops_past_node'] = default_cops_past_node
    request.session['rob_cur_node'] = int(random_nodes[-1])
    request.session['rob_path'] = []

# Init map inform
def initMapInform(request):
    request.session['turn'] = default_turn
    randomStartNode(request)
    request.session['is_rob_turn'] = default_is_rob_turn

    return render(request, 'sitemap/map.html')