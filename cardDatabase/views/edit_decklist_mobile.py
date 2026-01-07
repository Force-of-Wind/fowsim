from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, reverse, render
from django.utils import timezone

from cardDatabase.forms import SearchForm, AdvancedSearchForm
from cardDatabase.models import DeckList, DeckListCard, Format, TournamentPlayer
from cardDatabase.models.DeckList import UserDeckListZone
from fowsim.decorators import mobile_only

from cardDatabase.views.utils.search_context import get_search_form_ctx

from fowsim import constants as CONS


@login_required
@mobile_only
def get(request, decklist_id=None):
    # Check that the user matches the decklist
    decklist = get_object_or_404(DeckList, pk=decklist_id, profile__user=request.user)

    if decklist.deck_lock == CONS.MODE_TOURNAMENT:
        return HttpResponseRedirect(reverse("cardDatabase-tournament-decklist"))

    tournament_player = TournamentPlayer.objects.filter(profile=request.user.profile, deck=decklist).first()

    if tournament_player is not None:
        tournament = tournament_player.tournament
        deck_edit_locked = tournament.deck_edit_locked

        over_edit_deadline = True
        if (
            tournament.deck_edit_deadline is None
            or tournament.deck_edit_deadline.timestamp() > timezone.now().timestamp()
        ):
            over_edit_deadline = False

        if deck_edit_locked or over_edit_deadline:
            return HttpResponseRedirect(reverse("cardDatabase-tournament-decklist"))

    ctx = get_search_form_ctx()
    ctx["basic_form"] = SearchForm()
    ctx["advanced_form"] = AdvancedSearchForm()
    ctx["zones"] = UserDeckListZone.objects.filter(decklist__pk=decklist.pk).order_by(
        "-zone__show_by_default", "position"
    )
    ctx["decklist_cards"] = DeckListCard.objects.filter(decklist__pk=decklist.pk)
    ctx["decklist"] = decklist
    ctx["deck_formats"] = Format.objects.all()
    return render(request, "cardDatabase/html/edit_decklist_mobile.html", context=ctx)
