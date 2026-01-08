from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from cardDatabase.models import DeckList


@login_required
@require_POST
def post(request, decklist_id=None):
    # Check user matches the decklist
    decklist = get_object_or_404(DeckList, pk=decklist_id, profile__user=request.user)
    decklist.shareMode = ""
    decklist.shareCode = ""
    decklist.save()

    return JsonResponse({"decklist_pk": decklist.pk})
