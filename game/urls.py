from django.conf import settings
from django.urls import path

from . import views

urlpatterns = [
    #path('', views.index, name='index'),
    path('game_room/<str:room_name>/', views.game_room, name='game_room')
]