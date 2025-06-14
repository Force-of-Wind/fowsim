import json

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from cardDatabase.models.Tournament import Tournament, TournamentPlayer, TournamentStaff

@login_required
@require_POST
def post(request, tournament_id, player_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    staff_account = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staff_account is None or not staff_account.role.can_write:
        return JsonResponse({'error': 'Not authorized'}, status=401)
    
    tournamentPlayer = get_object_or_404(TournamentPlayer, tournament=tournament, pk=player_id)

    tournamentPlayer.deck.decklist = ''
    tournamentPlayer.deck.shareMode = ''
    tournamentPlayer.deck.deck_lock = ''

    tournamentPlayer.deck.save()
        
    tournamentPlayer.delete()

    return JsonResponse({'success':True})

