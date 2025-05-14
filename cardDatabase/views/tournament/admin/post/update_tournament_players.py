import json

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .....models.Tournament import Tournament, TournamentPlayer, TournamentStaff

@login_required
@require_POST
def post(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    updated_players = json.loads(request.body)

    staff_account = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staff_account is None or not staff_account.role.can_write:
        return JsonResponse({'error': 'Not authorized'}, status=401)
    
    if updated_players is None:
        return JsonResponse({'error': 'Payload incorrect'}, status=400)
        
    for updatedPlayer in updated_players:
        dbPlayer = TournamentPlayer.objects.get(pk=updatedPlayer['id'])
        dbPlayer.dropped_out = updatedPlayer['dropped']
        dbPlayer.notes = updatedPlayer['notes']
        dbPlayer.standing = updatedPlayer['standing']
        dbPlayer.registration_status = updatedPlayer['status']
        dbPlayer.save()

    return JsonResponse({'success':True})

