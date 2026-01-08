from django.shortcuts import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from cardDatabase.models import DeckList, DeckListZone, Format
from cardDatabase.models.DeckList import UserDeckListZone


@login_required
def get(request, format):
    decklist = DeckList.objects.create(
        profile=request.user.profile, name="Untitled Deck", deck_format=Format.objects.get(name=format)
    )
    for default_zone in DeckListZone.objects.filter(show_by_default=True, formats__name=format):
        UserDeckListZone.objects.create(zone=default_zone, position=default_zone.position, decklist=decklist)
    if request.user_agent.is_mobile or request.user_agent.is_tablet:
        return HttpResponseRedirect(reverse("cardDatabase-edit-decklist-mobile", kwargs={"decklist_id": decklist.id}))
    else:
        return HttpResponseRedirect(reverse("cardDatabase-edit-decklist", kwargs={"decklist_id": decklist.id}))
