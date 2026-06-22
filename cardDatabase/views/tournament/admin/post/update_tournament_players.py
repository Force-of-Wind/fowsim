import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from cardDatabase.models.Tournament import TournamentPlayer

from fowsim.decorators import tournament_admin


@login_required
@require_POST
@tournament_admin
def post(request, tournament_id):
    updated_players = json.loads(request.body)

    if updated_players is None:
        return JsonResponse({"error": "Payload incorrect"}, status=400)

    for updatedPlayer in updated_players:
        # Scope the lookup to this tournament so an admin of one tournament
        # cannot modify players belonging to another via a crafted payload.
        dbPlayer = TournamentPlayer.objects.filter(tournament=request.tournament, pk=updatedPlayer["id"]).first()
        if dbPlayer is None:
            continue
        dbPlayer.dropped_out = updatedPlayer["dropped"]
        dbPlayer.notes = updatedPlayer["notes"]
        dbPlayer.standing = updatedPlayer["standing"]
        dbPlayer.registration_status = updatedPlayer["status"]
        dbPlayer.last_registration_updated_by = request.user.profile
        dbPlayer.save()

    return JsonResponse({"success": True})
