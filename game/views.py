from django.shortcuts import render


def index(request):
    return render(request, 'game/html/index.html', {})


def game_room(request, room_name):
    return render(request, 'game/html/game_room.html', {
        'room_name': room_name
    })
