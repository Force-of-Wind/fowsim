from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from fowsim.decorators import tournament_reader


@login_required
@tournament_reader
def get(request, tournament_id):
    tournament = request.tournament
    
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