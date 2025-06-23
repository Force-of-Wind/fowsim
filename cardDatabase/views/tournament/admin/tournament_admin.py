from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from fowsim.decorators import tournament_reader

from cardDatabase.models.Tournament import TournamentStaff, TournamentPlayer, StaffRole

@login_required
@tournament_reader
def get(request, tournament_id):
    tournament = request.tournament
    
    deck_edit_locked = tournament.deck_edit_locked

    over_edit_deadline = True

    if tournament.deck_edit_deadline is None or tournament.deck_edit_deadline.timestamp() > timezone.now().timestamp():
        over_edit_deadline = False

    ruler_export = {}
    for player in TournamentPlayer.objects.filter(tournament=tournament):
        ruler_names = []
        if not player.deck.get_deck_rulers:
            continue
        rulers = player.deck.get_deck_rulers.order_by('card__name')
        for ruler in rulers:
            ruler_names.append(ruler.card.name)
        ruler_combo_name = ' + '.join(ruler_names)
        if ruler_combo_name in ruler_export:
            qty = ruler_export[ruler_combo_name]
            ruler_export[ruler_combo_name] = qty + 1
        else:
            ruler_export[ruler_combo_name] = 1

    tournament_staff = None
    staff_roles = None

    if staff_account.role.can_delete:
        tournament_staff = TournamentStaff.objects.filter(tournament = tournament)
        staff_roles = StaffRole.objects.filter(can_delete=False)

    return render(request, 'tournament/tournament_admin.html', context={
        'tournament': tournament,
        'staffAccount' : staff_account,
        'tournamentStaff': tournament_staff,
        'staffRoles': staff_roles,
        'deckEditLocked': deck_edit_locked,
        'overEditDeadline': over_edit_deadline,
        'rulerExport': ruler_export
    })