from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

from cardDatabase.models.Tournament import TournamentLevel
from cardDatabase.models.Banlist import Format

from fowsim.decorators import tournament_owner


@login_required
@tournament_owner
def get(request, tournament_id):
    if not request.user.profile.can_create_tournament:
        return HttpResponseRedirect(reverse("cardDatabase-tournament-create-unauthorized"))

    return render(
        request,
        "tournament/tournament_create.html",
        context={
            "meta_data": request.tournament.meta_data,
            "formats": Format.objects.all().order_by("pk"),
            "levels": TournamentLevel.objects.all(),
            "tournament": request.tournament,
        },
    )
