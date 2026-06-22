from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from cardDatabase.models.Tournament import TournamentPlayer

from fowsim.decorators import tournament_reader, tournament_admin


@login_required
@tournament_reader
def get(request, tournament_id):
    tournament = request.tournament

    player_qs = tournament.players.order_by("standing").all()
    other_notes_profiles = get_profiles_with_other_notes(tournament, player_qs, request.staff_account.role)

    players = map_tournament_player(player_qs, other_notes_profiles)

    return JsonResponse(players, safe=False)


@login_required
@tournament_reader
def getHtml(request, tournament_id):
    tournament = request.tournament
    staff_account = request.staff_account

    player_qs = tournament.players.order_by("standing").all()
    other_notes_profiles = get_profiles_with_other_notes(tournament, player_qs, staff_account.role)

    players = map_tournament_player(player_qs, other_notes_profiles)

    asTable = request.GET.get("asTable", False)

    if asTable:
        return render(
            request,
            "tournament/admin/player_table_renderer.html",
            context={"tournament": tournament, "players": players, "staff": staff_account.role},
        )

    return render(
        request,
        "tournament/admin/player_renderer.html",
        context={"tournament": tournament, "players": players, "staff": staff_account.role},
    )


@login_required
@tournament_admin
def getOtherNotes(request, tournament_id, player_id):
    """Return the notes recorded for this player's person in OTHER tournaments.

    Restricted to staff who can write (Admins and Owners) — used for judging,
    since prior conduct can impact the current tournament.
    """
    tournament = request.tournament

    player = get_object_or_404(TournamentPlayer, tournament=tournament, pk=player_id)

    other_entries = (
        TournamentPlayer.objects.filter(profile=player.profile)
        .exclude(tournament=tournament)
        .exclude(notes="")
        .select_related("tournament")
        .order_by("-tournament__start_datetime")
    )

    notes = [
        {
            "tournament": entry.tournament.title,
            "tournamentId": entry.tournament_id,
            "notes": entry.notes,
            "standing": entry.standing,
            "droppedOut": entry.dropped_out,
        }
        for entry in other_entries
    ]

    first_name, last_name = get_player_name(player)

    return JsonResponse(
        {
            "playerName": f"{first_name} {last_name}".strip(),
            "username": player.profile.user.username,
            "notes": notes,
        }
    )


def get_player_name(player):
    first_name = ""
    last_name = ""
    for field in player.user_data:
        if field["name"] == "firstname":
            first_name = field["value"]
        elif field["name"] == "lastname":
            last_name = field["value"]
    return first_name, last_name


def get_profiles_with_other_notes(tournament, players, role):
    """Set of profile ids (among the given players) that have non-empty notes in
    another tournament. Only computed for staff who can write, so read-only staff
    never learn about cross-tournament notes."""
    if not getattr(role, "can_write", False):
        return set()

    profile_ids = {player.profile_id for player in players}
    if not profile_ids:
        return set()

    return set(
        TournamentPlayer.objects.filter(profile_id__in=profile_ids)
        .exclude(tournament=tournament)
        .exclude(notes="")
        .values_list("profile_id", flat=True)
    )


def map_tournament_player(players, profiles_with_other_notes=frozenset()):
    mappedPlayers = []

    for player in players:
        first_name, last_name = get_player_name(player)

        additional_info_fields = []
        for field in player.user_data:
            if field["name"] not in ("firstname", "lastname"):
                additional_info_fields.append(field)

        ruler_names = []
        ruler_combo_name = "Unknown"
        if player.deck.get_deck_rulers:
            rulers = player.deck.get_deck_rulers.order_by("card__name")
            for ruler in rulers:
                ruler_names.append(ruler.card.name)
            ruler_combo_name = " + ".join(ruler_names)

        playerObj = {
            "id": player.pk,
            "profileId": player.profile_id,
            "firstname": first_name,
            "lastname": last_name,
            "additionalInfoFields": additional_info_fields,
            "dropped": player.dropped_out,
            "notes": player.notes,
            "standing": player.standing,
            "status": player.registration_status,
            "username": player.profile.user.username,
            "decklistId": player.deck.pk,
            "decklistShareCode": player.deck.shareCode,
            "ruler": ruler_combo_name,
            "hasOtherNotes": player.profile_id in profiles_with_other_notes,
        }
        mappedPlayers.append(playerObj)

    return mappedPlayers
