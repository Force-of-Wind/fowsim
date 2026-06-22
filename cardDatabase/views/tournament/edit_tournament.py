from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from cardDatabase.models.Tournament import TournamentLevel
from cardDatabase.models.Banlist import Format
from cardDatabase.views.tournament import tournament_constants as TOURNAMENTCONS
from cardDatabase.views.tournament.utils.utilities import ensure_meta_field

from fowsim.decorators import tournament_admin


@login_required
@tournament_admin
def get(request, tournament_id, error=False):
    tournament = request.tournament
    # Make sure the venue map coordinate fields are present so the picker shows
    # up even for older tournaments saved before the map feature existed. They
    # are appended empty, so nothing changes until a pin is actually placed.
    meta_data = tournament.meta_data
    for coord_field in ("location_lat", "location_lng"):
        meta_data = ensure_meta_field(meta_data, TOURNAMENTCONS.TOURNAMENT_DEFAULT_META_DATA, coord_field)
    return render(
        request,
        "tournament/tournament_edit.html",
        context={
            "meta_data": meta_data,
            "formats": Format.objects.all().order_by("pk"),
            "levels": TournamentLevel.objects.all(),
            "tournament": tournament,
            "error": error,
        },
    )


@login_required
def error(request, tournament_id):
    return get(request, tournament_id, True)
