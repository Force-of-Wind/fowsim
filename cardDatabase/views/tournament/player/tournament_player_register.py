from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from datetime import datetime

from cardDatabase.models.Tournament import Tournament, TournamentPlayer
from cardDatabase.models.DeckList import DeckList
from fowsim import constants as CONS
from cardDatabase.views.tournament import tournament_constants as TOURNAMENTCONS

from cardDatabase.views.tournament.utils.utilities import check_value_is_meta_data, map_meta_data

import uuid

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

    deck_filter &= ~Q(shareMode=CONS.MODE_TOURNAMENT)
    
    deck_filter &= ~Q(deck_lock=CONS.MODE_TOURNAMENT)

    if tournament.format is not None:
        deck_filter &= Q(deck_format=tournament.format)

    available_decks = DeckList.objects.filter(deck_filter).order_by("-last_modified")

    return render(request, 'tournament/player/tournament_player_register.html', context={
        "tournament": tournament,
        "fields": fields,
        "available_decks": available_decks
    })

def post(request, tournament_id):
    if not request.method == "POST":
        raise Http404
    
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    player = TournamentPlayer.objects.filter(tournament=tournament, profile=request.user.profile).first()

    if player is not None:
        return render(request, 'tournament/player/tournament_player_already_registered.html')
    
    if datetime.now().timestamp() > tournament.registration_deadline.timestamp() or tournament.registration_locked:
        return render(request, 'tournament/player/tournament_player_register_denied.html')
    
    if tournament.is_online:
        metaFields = TOURNAMENTCONS.ONLINE_TOURNAMENT_DEFAULT_PLAYER_META_DATA
    else:
        metaFields = TOURNAMENTCONS.OFFLINE_TOURNAMENT_DEFAULT_PLAYER_META_DATA
    
    data = dict(request.POST)
    meta_data = []
    for fieldName, _ in data.items():
        if check_value_is_meta_data(fieldName, metaFields):
            meta_data.append(map_meta_data(fieldName, data.get(fieldName, [None])[0], metaFields))
    
    decklist_id = request.POST.get('decklist')

    deck_filter = Q(profile=request.user.profile)

    deck_filter &= Q(pk=decklist_id)

    deck_filter &= ~Q(shareMode=CONS.MODE_TOURNAMENT, deck_lock=CONS.MODE_TOURNAMENT)

    if tournament.format is not None:
        deck_filter &= Q(deck_format=tournament.format)

    decklist = DeckList.objects.filter(deck_filter).first()
    
    if decklist is None:
        raise Http404
    
    decklist.shareMode = CONS.MODE_TOURNAMENT
    decklist.shareCode = uuid.uuid4().hex

    if tournament.deck_edit_locked or datetime.now().timestamp() > tournament.deck_edit_deadline.timestamp():
        decklist.deck_lock = CONS.MODE_TOURNAMENT

    decklist.save()

    init_standing = TournamentPlayer.objects.filter(tournament=tournament).count() + 1
    
    TournamentPlayer.objects.create(
        profile = request.user.profile,
        tournament = tournament,
        registration_status = CONS.PLAYER_REGISTRATION_REQUESTED,
        last_registration_updated_by = request.user.profile,
        user_data = meta_data,
        notes = '',
        deck = decklist,
        standing = init_standing,
        dropped_out = False
    )

    return HttpResponseRedirect(reverse('cardDatabase-detail-tournament', kwargs={'tournament_id': tournament_id}))