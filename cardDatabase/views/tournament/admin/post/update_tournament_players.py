import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from cardDatabase.models.Tournament import Tournament, TournamentPlayer, TournamentStaff

from fowsim.decorators import tournament_admin

@login_required
@require_POST
@tournament_admin
def post(request, tournament_id):
    updated_players = json.loads(request.body)

    print(updated_players)
    
    if updated_players is None:
        return JsonResponse({'error': 'Payload incorrect'}, status=400)
        
    for updatedPlayer in updated_players:
        dbPlayer = TournamentPlayer.objects.get(pk=updatedPlayer['id'])
        dbPlayer.dropped_out = updatedPlayer['dropped']
        dbPlayer.notes = updatedPlayer['notes']
        dbPlayer.standing = updatedPlayer['standing']
        print(updatedPlayer['status'])
        dbPlayer.registration_status = updatedPlayer['status']
        dbPlayer.last_registration_updated_by = request.user.profile
        dbPlayer.save()

    return JsonResponse({'success':True})

