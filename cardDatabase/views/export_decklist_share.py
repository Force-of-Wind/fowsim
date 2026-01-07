from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from cardDatabase.models import DeckList
from . import generate_decklist


def get(request, decklist_id, share_parameter):
    decklist = get_object_or_404(DeckList, id=decklist_id, shareCode=share_parameter, public=False)
    return generate_decklist.get(decklist)
