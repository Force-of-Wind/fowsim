from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from ...models.Tournament import Tournament, TournamentPlayer, TournamentStaff
from fowsim import constants as CONS

def get(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    players = TournamentPlayer.objects.filter(tournament=tournament, registration_status=CONS.PLAYER_REGISTRATION_COMPLETED).order_by('standing')

    player_counter = players.count()

    current_player = TournamentPlayer.objects.filter(tournament=tournament, profile=request.user.profile).first()

    staff_account = TournamentStaff.objects.filter(tournament = tournament, profile=request.user.profile).first()

    is_staff = staff_account is not None and staff_account.role.can_read

    registration_open = False

    if(tournament.phase == CONS.TOURNAMENT_PHASE_REGISTRATION and not tournament.registration_locked and tournament.registration_deadline > timezone.now()):
        registration_open = True
    

    return render(request, 'tournament/tournament_detail.html', context={
        'tournament': tournament,
        'players':players,
        'playerCount': player_counter,
        'currentPlayer': current_player,
        'isStaff': is_staff,
        'registrationOpen': registration_open
    })