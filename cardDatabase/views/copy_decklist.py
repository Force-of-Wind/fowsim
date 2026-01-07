from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

from cardDatabase.models import DeckList, DeckListCard
from cardDatabase.models.DeckList import UserDeckListZone


@login_required
def get(request, decklist_id=None):
    try:
        original_decklist = DeckList.objects.get(pk=decklist_id)
    except DeckList.DoesNotExist:
        return HttpResponseRedirect(reverse("cardDatabase-user-decklists"))

    new_decklist = DeckList.objects.create(
        profile=request.user.profile, name=original_decklist.name, comments=original_decklist.comments
    )
    cards = DeckListCard.objects.filter(decklist__pk=original_decklist.pk)
    original_zones = UserDeckListZone.objects.filter(decklist__pk=original_decklist.pk)

    for zone in original_zones:
        UserDeckListZone.objects.create(decklist=new_decklist, position=zone.position, zone=zone.zone)

    for card in cards:
        zone = UserDeckListZone.objects.get(decklist=new_decklist, position=card.zone.position, zone=card.zone.zone)
        DeckListCard.objects.create(
            decklist=new_decklist, card=card.card, position=card.position, zone=zone, quantity=card.quantity
        )

    if request.user_agent.is_mobile or request.user_agent.is_tablet:
        return HttpResponseRedirect(
            reverse("cardDatabase-edit-decklist-mobile", kwargs={"decklist_id": new_decklist.pk})
        )
    else:
        return HttpResponseRedirect(reverse("cardDatabase-edit-decklist", kwargs={"decklist_id": new_decklist.pk}))
