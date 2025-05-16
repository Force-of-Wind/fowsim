from django.shortcuts import render

def get(request):
    return render(request, 'tournament/tournament_create_unauthorized.html')