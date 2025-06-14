from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST


from cardDatabase.models.Tournament import Tournament, TournamentStaff, TournamentPlayer

from fowsim import constants as CONS

@login_required
@require_POST
def post (request, tournament_id):
    
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    staff_account = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staff_account is None or not staff_account.role.can_write:
        return JsonResponse({'error': 'Not authorized'}, status=401)
    
    tournament.phase = CONS.TOURNAMENT_PHASE_CREATED
    tournament.save()

    for player in TournamentPlayer.objects.filter(tournament=tournament):
            player.deck.deck_lock = ''
            player.deck.save()

    return JsonResponse({ 'success': True })