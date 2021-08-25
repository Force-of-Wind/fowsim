from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    return render(request, 'game/html/index.html', {})


@login_required
def game_room(request, room_name):
    return render(request, 'game/html/game_room.html', {
        'room_name': room_name
    })
