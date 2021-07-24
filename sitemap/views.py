from django.shortcuts import render
from django.http import HttpResponse
import folium
from folium.features import DivIcon
from branca.element import Element

import json
from collections import OrderedDict

import pandas as pd
import sqlite3

cop_cur_node = 1400002600 # 금정구청
rob_cur_node = 1400002900 # 금정경찰서교차로

turn = 1

is_rob_turn = True

node_df = pd.DataFrame()

# map 구성
def initMap():
    global node_df

    # read node data from database
    engine = sqlite3.connect('./db.sqlite3')
    node_df = pd.read_sql('SELECT * FROM node_information', engine, index_col='nodeId')
    node_df['linkedNode'] = node_df['linkedNode'].apply(lambda x : json.loads(x)) # json to list

    # Create map,   지도 중심 금정구청으로 잡음
    m = folium.Map(location=[35.243603319969786, 129.09212543391874], zoom_start=15)

    # draw graph on map
    for row_index, row in node_df.iterrows():
        enode_list = row['linkedNode']
        for enode in enode_list:
            fnode_point = [row['latitude'], row['longitude']]
            enode_point = [node_df.loc[enode, 'latitude'], node_df.loc[enode, 'longitude']]
            folium.PolyLine([fnode_point, enode_point]).add_to(m)
    
    # json file에 저장할 dictionary 만들기 (temp)
    linked_node_data = OrderedDict()

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
            linked_node_data[i] = linked_node_id

    # json 파일로 저장
    with open('linkedNode.json', 'w', encoding="utf-8") as make_file:
        json.dump(linked_node_data, make_file, ensure_ascii=False, indent='\t')
    
    # Show Cop and Robber location (temp)
    folium.Marker([node_df.loc[rob_cur_node, 'latitude'], node_df.loc[rob_cur_node, 'longitude']], icon=folium.Icon(icon='car', prefix='fa', color = 'red')).add_to(m)
    folium.Marker([node_df.loc[cop_cur_node, 'latitude'], node_df.loc[cop_cur_node, 'longitude']], icon=folium.Icon(icon='star', color = 'blue')).add_to(m)

    # Get html representation of map
    m = m._repr_html_()
    return m


def map(request):

    global is_rob_turn, cop_cur_node
    
    context = {
        'm': initMap(),
        'turn' : turn,
        'is_rob_turn' : is_rob_turn,
        'linked_node_num' : len(node_df.loc[rob_cur_node, 'linkedNode']),
        'is_finish' : cop_cur_node==rob_cur_node,
    }

    return render(request, 'map.html', context)

# Change Cop/Robber location
def moveNextNode(request):
    global is_rob_turn, cop_cur_node

    if is_rob_turn:
        global turn 
        turn = turn + 1

        global rob_cur_node

        with open('linkedNode.json') as json_file:
            json_data = json.load(json_file)
            rob_cur_node = json_data[request.POST['next_node'].__str__()]
        
        is_rob_turn = False

    else:
        cop_cur_node = node_df.loc[cop_cur_node, 'linkedNode'][0]
        is_rob_turn = True

    return render(request, 'map.html')

# Init map inform
def initMapInform(request):

    global turn, cop_cur_node, rob_cur_node, is_rob_turn
    turn = 1
    cop_cur_node = 1400002600 # 금정구청
    rob_cur_node = 1400002900 # 금정경찰서교차로
    is_rob_turn = True

    return render(request, 'map.html')