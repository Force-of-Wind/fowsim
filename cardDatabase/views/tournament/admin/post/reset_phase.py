from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from cardDatabase.models.Tournament import TournamentPlayer

from fowsim import constants as CONS
from fowsim.decorators import tournament_admin


@login_required
@require_POST
@tournament_admin
def post(request, tournament_id):
    tournament = request.tournament

    tournament.phase = CONS.TOURNAMENT_PHASE_CREATED
    tournament.save()

    for player in TournamentPlayer.objects.filter(tournament=tournament):
        player.deck.deck_lock = ""
        player.deck.save()

    return JsonResponse({"success": True})
