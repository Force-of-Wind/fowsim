from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.views.decorators.http import require_POST
from datetime import datetime

from cardDatabase.models.Tournament import Tournament, TournamentPlayer
from cardDatabase.models.DeckList import DeckList
from fowsim import constants as CONS

import uuid


@login_required
def get(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    player = TournamentPlayer.objects.filter(tournament=tournament, profile=request.user.profile).first()

    timestamp = datetime.now().timestamp()

    if timestamp > tournament.deck_edit_deadline.timestamp() or tournament.deck_edit_locked or timestamp > tournament.start_datetime.timestamp():
        return render(request, "tournament/player/tournament_deck_change_denied.html")

    deck_filter = Q(profile=request.user.profile)

    deck_filter &= ~Q(pk=player.deck.pk)

    deck_filter &= ~Q(shareMode=CONS.MODE_TOURNAMENT)

    deck_filter &= ~Q(deck_lock=CONS.MODE_TOURNAMENT)

    if tournament.format is not None:
        deck_filter &= Q(deck_format=tournament.format)

    available_decks = DeckList.objects.filter(deck_filter).order_by("-last_modified")

    return render(
        request,
        "tournament/player/tournament_deck_change.html",
        context={"tournament": tournament, "available_decks": available_decks},
    )


@require_POST
def post(request, tournament_id):
    if not request.method == "POST":
        raise Http404

    tournament = get_object_or_404(Tournament, pk=tournament_id)

    player = TournamentPlayer.objects.filter(tournament=tournament, profile=request.user.profile).first()

    timestamp = datetime.now().timestamp()

    if timestamp > tournament.deck_edit_deadline.timestamp() or tournament.deck_edit_locked or timestamp > tournament.start_datetime.timestamp():
        return render(request, "tournament/player/tournament_deck_change_denied.html")

    decklist_id = request.POST.get("decklist")

    if decklist_id == player.deck.pk:
        return render(request, "tournament/player/tournament_deck_change_denied.html")

    deck_filter = Q(profile=request.user.profile)

    deck_filter &= Q(pk=decklist_id)

    deck_filter &= ~Q(shareMode=CONS.MODE_TOURNAMENT, deck_lock=CONS.MODE_TOURNAMENT)

    if tournament.format is not None:
        deck_filter &= Q(deck_format=tournament.format)

    decklist = DeckList.objects.filter(deck_filter).first()

    if decklist is None:
        raise Http404

    # reset old decklist
    player.deck.shareMode = ""
    player.deck.shareCode = ""
    player.deck.deck_lock = ""
    player.deck.save()

    decklist.shareMode = CONS.MODE_TOURNAMENT
    decklist.shareCode = uuid.uuid4().hex

    if tournament.deck_edit_locked or datetime.now().timestamp() > tournament.deck_edit_deadline.timestamp():
        decklist.deck_lock = CONS.MODE_TOURNAMENT

    decklist.save()

    player.last_registration_updated_by = request.user.profile
    player.deck = decklist

    player.save()

    return HttpResponseRedirect(reverse("cardDatabase-detail-tournament", kwargs={"tournament_id": tournament_id}))
