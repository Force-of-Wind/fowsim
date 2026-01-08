from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

import json

from cardDatabase.models import Format, DeckList, Card, TournamentPlayer
from cardDatabase.models.DeckList import UserDeckListZone, DeckListCard, DeckListZone

from fowsim import constants as CONS


@login_required
@require_POST
def post(request, decklist_id=None):
    data = json.loads(request.body.decode("UTF-8"))
    decklist_data = data["decklist_data"]
    decklist_format = data["deck_format"]
    if "is_public" in data:
        is_public = data["is_public"]
    else:
        is_public = True

    # Check user matches the decklist
    decklist = get_object_or_404(DeckList, pk=decklist_id, profile__user=request.user)

    if decklist.deck_lock == CONS.MODE_TOURNAMENT:
        return HttpResponse("Deck is in tournament mode and cannot be edited!", status=400)

    tournament_player = TournamentPlayer.objects.filter(profile=request.user.profile, deck=decklist).first()

    if tournament_player is not None:
        tournament = tournament_player.tournament
        deck_edit_locked = tournament.deck_edit_locked

        over_edit_deadline = True
        if (
            tournament.deck_edit_deadline is None
            or tournament.deck_edit_deadline.timestamp() > timezone.now().timestamp()
        ):
            over_edit_deadline = False

        if deck_edit_locked or over_edit_deadline:
            return HttpResponse("Deck is in tournament mode and cannot be edited!", status=400)

    decklist.name = decklist_data["name"]
    decklist.comments = decklist_data["comments"]
    decklist.public = is_public
    decklist.deck_format = Format.objects.get(name=decklist_format)
    # reset state if public since public decklists cant have share codes
    if is_public and not tournament_player:
        decklist.shareMode = ""
        decklist.shareCode = ""
    decklist.save()
    #  Remove old cards, then rebuild it
    DeckListCard.objects.filter(decklist__pk=decklist.pk).delete()
    UserDeckListZone.objects.filter(decklist__pk=decklist.pk).delete()
    zone_count = 0
    for zone_data in decklist_data["zones"]:
        zone, created = DeckListZone.objects.get_or_create(name=zone_data["name"])
        user_zone, created = UserDeckListZone.objects.get_or_create(zone=zone, position=zone_count, decklist=decklist)
        for card_data in zone_data["cards"]:
            card = Card.objects.get(card_id=card_data["id"])
            try:
                DeckListCard.objects.get_or_create(
                    decklist=decklist,
                    card=card,
                    position=card_data["position"],
                    zone=user_zone,
                    quantity=card_data["quantity"],
                )
            except ValueError:  # Probably user input error somehow, like putting 'e' in the quantity
                pass
        zone_count += 1

    return JsonResponse({"decklist_pk": decklist.pk})
