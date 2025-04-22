import json

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


from ...models.Tournament import Tournament, TournamentLevel, TournamentPlayer, TournamentStaff, StaffRole
from fowsim import constants as CONS
from . import tournament_constants as TOURNAMENTCONS


@login_required
def update_tournament_phase(request, tournament_id):
    updatedState = request.POST.get('status')
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    staffAccount = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staffAccount is None or not staffAccount.role.can_delete:
        return JsonResponse({'error': 'Not authorized'}, status=401)
    
    if updatedState is None:
        return JsonResponse({'error': 'Payload incorrect'}, status=400)
    
    tournament.phase = updatedState
    tournament.save()

    return JsonResponse({}, status=200)


@login_required
def get_tournament_players(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    staffAccount = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staffAccount is None or not staffAccount.role.can_read:
        return JsonResponse({'error': 'Not authorized'}, status=401)
    
    players = []

    for player in tournament.players.all():
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

@login_required
def update_tournament_players(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    updatedPlayers = json.loads(request.body)

    staffAccount = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staffAccount is None or not staffAccount.role.can_write:
        return JsonResponse({'error': 'Not authorized'}, status=401)
    
    if updatedPlayers is None:
        return JsonResponse({'error': 'Payload incorrect'}, status=400)
        
    for updatedPlayer in updatedPlayers:
        dbPlayer = TournamentPlayer.get(pk=updatedPlayer.id)
        dbPlayer.dropped_out = updatedPlayer.dropped
        dbPlayer.notes = updatedPlayer.notes
        dbPlayer.standing = updatedPlayer.standing
        dbPlayer.registration_status = updatedPlayer.status
        dbPlayer.save()

    return JsonResponse()

