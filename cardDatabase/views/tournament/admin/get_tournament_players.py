from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from cardDatabase.models.Tournament import Tournament, TournamentStaff


@login_required
def get(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    staff_account = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staff_account is None or not staff_account.role.can_read:
        return JsonResponse({'error': 'Not authorized'}, status=401)
    
    players = []

    for player in tournament.players.order_by('standing').all():
        playerObj = {
            "id": player.pk,
            "dropped": player.dropped_out,
            "userData": player.user_data,
            "notes": player.notes,
            "standing": player.standing,
            "status": player.registration_status,
            "username": player.profile.user.username,
            "decklistId": player.deck.pk,
            "decklistShareCode": player.deck.shareCode,
        }
        players.append(playerObj)

    return JsonResponse(players, safe=False)