import json
import re
import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, F, Count
from django.forms.fields import MultipleChoiceField
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse


from ..forms import SearchForm, AdvancedSearchForm, AddCardForm, UserRegistrationForm, DecklistSearchForm
from ..models.Tournament import Tournament, TournamentLevel, TournamentPlayer, TournamentStaff, StaffRole
from ..models.Banlist import Format
from fowsim import constants as CONS
from . import tournament_constants as TOURNAMENTCONS


@login_required
def update_tournament_phase(request, tournament_id):
    updatedState = request.POST.get('status')
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    staffAccount = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staffAccount is None or not staffAccount.role.can_delete:
        return JsonResponse({'error': 'Not authorized'}, status=401)
    
    if updatedState is None:
        return JsonResponse({'error': 'Payload incorrect'}, status=400)
    
    tournament.phase = updatedState
    tournament.save()

    return JsonResponse({}, status=200)


@login_required
def get_tournament_players(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    staffAccount = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staffAccount is None or not staffAccount.role.can_read:
        return JsonResponse({'error': 'Not authorized'}, status=401)
    
    players = []

    for player in tournament.players.all():
        playerObj = {
            "id": player.pk,
            "dropped": player.dropped_out,
            "userData": player.user_data,
            "notes": player.notes,
            "standing": player.standing,
            "status": player.registration_status,
            "username": player.profile.user.username,
            "decklistId": player.deck.pk,
            "decklistShareCode": player.deck.shareCode,
        }
        players.append(playerObj)

    return JsonResponse(players, safe=False)

