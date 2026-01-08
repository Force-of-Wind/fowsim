from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from django.views.decorators.http import require_POST

from fowsim.decorators import tournament_admin


@login_required
@require_POST
@tournament_admin
def post(request, tournament_id):
    tournament = request.tournament

    data = dict(request.POST)

    reveal_state = "revealState" in data

    if tournament.reveal_decklists != reveal_state:
        tournament.reveal_decklists = reveal_state
        tournament.save()

    return JsonResponse({"success": True})
