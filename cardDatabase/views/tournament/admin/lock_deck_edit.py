from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404

from ....models.Tournament import Tournament, TournamentStaff

@login_required
def post (request, tournament_id):
    if not request.method == "POST":
        raise Http404
    
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    staff_account = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staff_account is None or not staff_account.role.can_write:
        return JsonResponse({'error': 'Not authorized'}, status=401)
    
    data = dict(request.POST)
    
    lock_state = 'lockState' in data
    
    if tournament.deck_edit_locked != lock_state:
        tournament.deck_edit_locked = lock_state
        #update the lock state on each deck
        tournament.save()

    return JsonResponse({'success': True})