from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

from fowsim.decorators import tournament_owner


@login_required
@tournament_owner
def get(request, tournament_id):
    tournament = request.tournament

    tournament.delete()

    return HttpResponseRedirect(reverse("cardDatabase-tournament-list"))
