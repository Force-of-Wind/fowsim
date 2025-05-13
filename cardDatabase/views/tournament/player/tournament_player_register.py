import json

from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime

from ....models.Tournament import Tournament, TournamentLevel, TournamentPlayer, TournamentStaff, StaffRole
from ....models.DeckList import DeckList
from fowsim import constants as CONS
from .. import tournament_constants as TOURNAMENTCONS

@login_required
def get(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    player = TournamentPlayer.objects.filter(tournament=tournament, profile=request.user.profile).first()

    if player is not None:
        return render(request, 'tournament/player/tournament_player_already_registered.html')
    
    if datetime.now().timestamp() > tournament.registration_deadline.timestamp() or tournament.registration_locked:
        return render(request, 'tournament/player/tournament_player_register_denied.html')

    fields = TOURNAMENTCONS.OFFLINE_TOURNAMENT_DEFAULT_PLAYER_META_DATA

    if tournament.is_online:
        fields = TOURNAMENTCONS.ONLINE_TOURNAMENT_DEFAULT_PLAYER_META_DATA

    deck_filter = Q(profile=request.user.profile)

    deck_filter &= ~Q(shareMode=CONS.MODE_TOURNAMENT, deck_lock=CONS.MODE_TOURNAMENT)

    if tournament.format is not None:
        deck_filter &= Q(deck_format=tournament.format)

    available_decks = DeckList.objects.filter(deck_filter).order_by("-last_modified")

    return render(request, 'tournament/player/tournament_player_register.html', context={
        "tournament": tournament,
        "fields": fields,
        "available_decks": available_decks
    })