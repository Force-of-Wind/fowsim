from django.shortcuts import render

def get(request):
    return render(request, 'tournament/tournament_decklist_locked.html')