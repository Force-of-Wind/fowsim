from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from cardDatabase.models.Tournament import TournamentPlayer

from fowsim.decorators import tournament_admin

@login_required
@require_POST
@tournament_admin
def post(request, tournament_id, player_id):
    tournament = request.tournament

    tournamentPlayer = get_object_or_404(TournamentPlayer, tournament=tournament, pk=player_id)

    tournamentPlayer.deck.shareMode = ''
    tournamentPlayer.deck.deck_lock = ''

    tournamentPlayer.deck.save()
        
    tournamentPlayer.delete()

    return JsonResponse({'success':True})

