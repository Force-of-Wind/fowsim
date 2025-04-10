from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

import json
import uuid

from cardDatabase.models import DeckList


@login_required
@require_POST
def post(request, decklist_id=None):
    mode = 'private'

    # Check user matches the decklist
    decklist = get_object_or_404(DeckList, pk=decklist_id, profile__user=request.user)
    decklist.shareMode = mode
    decklist.shareCode = uuid.uuid4().hex
    decklist.save()

    return JsonResponse({'code': decklist.shareCode})
