from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from cardDatabase.models.Tournament import TournamentLevel
from cardDatabase.models.Banlist import Format

from fowsim.decorators import tournament_admin


@login_required
@tournament_admin
def get(request, tournament_id, error=False):
    tournament = request.tournament
    return render(
        request,
        "tournament/tournament_edit.html",
        context={
            "meta_data": tournament.meta_data,
            "formats": Format.objects.all().order_by("pk"),
            "levels": TournamentLevel.objects.all(),
            "tournament": tournament,
            "error": error,
        },
    )


@login_required
def error(request, tournament_id):
    return get(request, tournament_id, True)
