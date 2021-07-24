from django.shortcuts import render
from django.http import HttpResponse
import folium
from folium.features import DivIcon
from branca.element import Element

import json
from collections import OrderedDict

# Node 클래스 정의(임의로 넣음)
class Node:
    latitude: float = None
    longitude: float = None
    linked_node: list = []
    def setData(self, _latitude, _longtitude, _linked_node):
        self.latitude = _latitude
        self.longitude = _longtitude
        self.linked_node = _linked_node

cop_cur_node = 1
rob_cur_node = 4

turn = 1

is_rob_turn = True

# node dictionary 만들기 (temp)
node_dict = {}

# map 구성
def initMap():
    # 임의로 5개 노드 추가 (temp)
    node_dict[1] = Node()
    node_dict[1].setData(35.27365638258647, 129.08935019105886, [5, 2])
    node_dict[2] = Node()
    node_dict[2].setData(35.263371, 129.078558, [1, 3])
    node_dict[3] = Node()
    node_dict[3].setData(35.251492, 129.075381, [2, 4])
    node_dict[4] = Node()
    node_dict[4].setData(35.242620, 129.103036, [3, 5])
    node_dict[5] = Node()
    node_dict[5].setData(35.265300, 129.109705, [4, 1])

    # Create map,   지도 중심 금정구청으로 잡음
    m = folium.Map(location=[35.243603319969786, 129.09212543391874], zoom_start=13)

    # Show entire edge (temp)
    folium.PolyLine([[node_dict[1].latitude, node_dict[1].longitude],[node_dict[2].latitude, node_dict[2].longitude]]).add_to(m)
    folium.PolyLine([[node_dict[2].latitude, node_dict[2].longitude],[node_dict[3].latitude, node_dict[3].longitude]]).add_to(m)
    folium.PolyLine([[node_dict[3].latitude, node_dict[3].longitude],[node_dict[4].latitude, node_dict[4].longitude]]).add_to(m)
    folium.PolyLine([[node_dict[4].latitude, node_dict[4].longitude],[node_dict[5].latitude, node_dict[5].longitude]]).add_to(m)
    folium.PolyLine([[node_dict[5].latitude, node_dict[5].longitude],[node_dict[1].latitude, node_dict[1].longitude]]).add_to(m)

    # json file에 저장할 dictionary 만들기 (temp)
    linked_node_data = OrderedDict()

    # Show nodes that can be moved by a thief.
    if is_rob_turn:
        for i in range(0, len(node_dict[rob_cur_node].linked_node)):
            linked_node_id = node_dict[rob_cur_node].linked_node[i]
            folium.Marker([node_dict[linked_node_id].latitude, node_dict[linked_node_id].longitude], 
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
    folium.Marker([node_dict[rob_cur_node].latitude, node_dict[rob_cur_node].longitude], icon=folium.Icon(icon='car', prefix='fa', color = 'red')).add_to(m)
    folium.Marker([node_dict[cop_cur_node].latitude, node_dict[cop_cur_node].longitude], icon=folium.Icon(icon='star', color = 'blue')).add_to(m)

    # Get html representation of map
    m = m._repr_html_()
    return m

# Create your views here.
def map(request):

    global is_rob_turn, cop_cur_node
    
    context = {
        'm': initMap(),
        'turn' : turn,
        'is_rob_turn' : is_rob_turn,
        'linked_node_num' : len(node_dict[rob_cur_node].linked_node),
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
        cop_cur_node = node_dict[cop_cur_node].linked_node[0]
        is_rob_turn = True

    return render(request, 'map.html')

# Init map inform
def initMapInform(request):

    global turn, cop_cur_node, rob_cur_node, is_rob_turn
    turn = 1
    cop_cur_node = 1
    rob_cur_node = 4
    is_rob_turn = True

    return render(request, 'map.html')