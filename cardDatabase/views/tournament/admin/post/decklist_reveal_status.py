from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404

from django.views.decorators.http import require_POST

from .....models.Tournament import Tournament, TournamentStaff

@login_required
@require_POST
def post (request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    staff_account = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staff_account is None or not staff_account.role.can_write:
        return JsonResponse({'error': 'Not authorized'}, status=401)
    
    data = dict(request.POST)
    
    reveal_state = 'revealState' in data
    
    if tournament.reveal_decklists != reveal_state:
        tournament.reveal_decklists = reveal_state
        tournament.save()

    return JsonResponse({'success': True})