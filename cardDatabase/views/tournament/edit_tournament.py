from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from cardDatabase.models.Tournament import Tournament, TournamentLevel, TournamentStaff
from cardDatabase.models.Banlist import Format

@login_required
def get(request, tournament_id, error = False):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    staff_account = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staff_account is None or not staff_account.role.can_write:
        return HttpResponse('Not authorized', 401)
    
    return render(request, 'tournament/tournament_edit.html', context={
        'meta_data': tournament.meta_data,
        'formats': Format.objects.all().order_by('pk'),
        'levels': TournamentLevel.objects.all(),
        'tournament': tournament,
        'error': error
    })

@login_required
def error(request, tournament_id):
    return get(request, tournament_id, True)