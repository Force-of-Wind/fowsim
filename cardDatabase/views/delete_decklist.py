from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from fowsim import constants as CONS

from cardDatabase.models import DeckList, TournamentPlayer


@csrf_exempt
@login_required
def get(request, decklist_id=None):
    if decklist_id:
        try:
            decklist = DeckList.objects.get(pk=decklist_id)
            if decklist.profile.user == request.user:  # Check they aren't deleting other people's lists
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
                decklist.delete()
        except DeckList.DoesNotExist:
            pass
    return HttpResponseRedirect(reverse("cardDatabase-user-decklists"))
