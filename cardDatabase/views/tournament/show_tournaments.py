from django.shortcuts import render

from ...models.Tournament import Tournament

def get(request):
    tournaments = Tournament.objects.order_by('-start_datetime').all()

    return render(request, 'tournament/tournament_list.html', context={
        "tournaments": tournaments
    })