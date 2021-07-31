from django.urls import path
from .import views

urlpatterns = [
    path('', views.map, name='map'),
    path('post/', views.moveNextNode, name='move_next_node'),
    path('init/', views.initMapInform, name='init_map_inform'),
]