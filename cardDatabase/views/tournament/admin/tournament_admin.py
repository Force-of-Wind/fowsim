from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone

from ....models.Tournament import Tournament, TournamentStaff

@login_required
def get(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    staff_account = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staff_account is None or not staff_account.role.can_write:
        return HttpResponse('Not authorized', 401)
    
    deck_edit_locked = tournament.deck_edit_locked

    over_edit_deadline = True

    if tournament.deck_edit_deadline is None or tournament.deck_edit_deadline.timestamp() > timezone.now().timestamp():
        over_edit_deadline = False

    return render(request, 'tournament/tournament_admin.html', context={
        'tournament': tournament,
        'staffAccount' : staff_account,
        'deckEditLocked': deck_edit_locked,
        'overEditDeadline': over_edit_deadline
    })