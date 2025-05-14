from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from ...models.Tournament import Tournament, TournamentPlayer

from fowsim import constants as CONS

@login_required
def get(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    
    tournamentPlayer = get_object_or_404(TournamentPlayer, tournament=tournament, profile=request.user.profile)
    
    if tournament.phase == CONS.TOURNAMENT_PHASE_REGISTRATION:
        tournamentPlayer.delete()

        return HttpResponseRedirect(reverse('cardDatabase-detail-tournament', kwargs={'tournament_id': tournament_id}))

    return HttpResponseRedirect(reverse('cardDatabase-tournament-remove-invalid'))