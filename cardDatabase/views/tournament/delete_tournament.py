from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from cardDatabase.models.Tournament import Tournament, TournamentStaff

@login_required
def get(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    staff_account = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staff_account is None or not staff_account.role.can_delete:
        return HttpResponse('Not authorized', 401)
    
    tournament.delete()

    return HttpResponseRedirect(reverse('cardDatabase-tournament-list'))