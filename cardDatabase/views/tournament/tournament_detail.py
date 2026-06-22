from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from cardDatabase.models.Tournament import Tournament, TournamentPlayer, TournamentStaff
from fowsim import constants as CONS


def _meta_value(meta_data, name):
    for field in meta_data or []:
        if field.get("name") == name:
            return field.get("value")
    return None


def _build_map_location(tournament):
    """Return {lat, lng, address} for in-person tournaments that have stored
    coordinates, otherwise None. Legacy tournaments saved before the venue map
    feature simply lack the coordinate fields and fall through to None, so they
    keep rendering their plain-text location."""
    if tournament.is_online:
        return None
    try:
        lat = float(_meta_value(tournament.meta_data, "location_lat"))
        lng = float(_meta_value(tournament.meta_data, "location_lng"))
    except (TypeError, ValueError):
        return None
    return {
        # Format as strings so locale number formatting never turns the decimal
        # point into a comma in URLs / data attributes.
        "lat": f"{lat:.6f}",
        "lng": f"{lng:.6f}",
        "address": _meta_value(tournament.meta_data, "location") or "",
    }


def get(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    current_player = None

    staff_account = None

    if request.user.is_authenticated:
        current_player = TournamentPlayer.objects.filter(tournament=tournament, profile=request.user.profile).first()
        staff_account = TournamentStaff.objects.filter(tournament=tournament, profile=request.user.profile).first()

    is_staff = staff_account is not None and staff_account.role.can_read

    registration_open = False

    if (
        tournament.phase == CONS.TOURNAMENT_PHASE_REGISTRATION
        and not tournament.registration_locked
        and tournament.registration_deadline > timezone.now()
    ):
        registration_open = True

    #Show all players during registration to make it more anticing for players to join
    if registration_open:
        players = TournamentPlayer.objects.filter(
            tournament=tournament
        ).order_by("standing")
    else:
        players = TournamentPlayer.objects.filter(
            tournament=tournament, registration_status=CONS.PLAYER_REGISTRATION_COMPLETED
        ).order_by("standing")

    player_counter = players.count()

    # Build an ordered list of phase steps so the template can render a progress
    # stepper that highlights where the tournament currently is.
    ordered_phases = [phase_value for phase_value, _ in CONS.TOURNAMENT_PHASES]
    try:
        current_phase_index = ordered_phases.index(tournament.phase)
    except ValueError:
        current_phase_index = -1

    phase_steps = []
    for index, phase_value in enumerate(ordered_phases):
        if index < current_phase_index:
            state = "done"
        elif index == current_phase_index:
            state = "active"
        else:
            state = "upcoming"
        phase_steps.append({"label": phase_value, "state": state})

    return render(
        request,
        "tournament/tournament_detail.html",
        context={
            "tournament": tournament,
            "players": players,
            "playerCount": player_counter,
            "currentPlayer": current_player,
            "isStaff": is_staff,
            "registrationOpen": registration_open,
            "phaseSteps": phase_steps,
            "mapLocation": _build_map_location(tournament),
        },
    )
