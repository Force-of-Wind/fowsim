import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime
    


from ....models.Tournament import Tournament, TournamentLevel, TournamentPlayer, TournamentStaff, StaffRole
from fowsim import constants as CONS
from .. import tournament_constants as TOURNAMENTCONS

@login_required
def get(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    player = TournamentPlayer.objects.filter(tournament=tournament, profile=request.user.profile).first()

    if player is not None:
        return render(request, 'tournament/player/tournament_player_already_registered.html')

    print(datetime.now().timestamp())
    print(tournament.registration_deadline.timestamp())
    print(datetime.now().timestamp() > tournament.registration_deadline.timestamp())
    
    if datetime.now().timestamp() > tournament.registration_deadline.timestamp() or tournament.registration_locked:
        return render(request, 'tournament/player/tournament_player_register_denied.html')

    fields = TOURNAMENTCONS.OFFLINE_TOURNAMENT_DEFAULT_PLAYER_META_DATA

    if tournament.is_online:
        fields = TOURNAMENTCONS.ONLINE_TOURNAMENT_DEFAULT_PLAYER_META_DATA

    return render(request, 'tournament/player/tournament_player_register.html', context={
        "tournament": tournament,
        "fields": fields
    })