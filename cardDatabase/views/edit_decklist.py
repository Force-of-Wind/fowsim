from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, reverse, render

from cardDatabase.forms import SearchForm, AdvancedSearchForm
from cardDatabase.models import DeckList, DeckListCard, Format
from cardDatabase.models.DeckList import UserDeckListZone
from cardDatabase.views.utils.search_context import get_search_form_ctx
from fowsim.decorators import desktop_only


@login_required
@desktop_only
def get(request, decklist_id=None):
    # Check that the user matches the decklist
    decklist = get_object_or_404(DeckList, pk=decklist_id, profile__user=request.user)

    if decklist.shareMode == "tournament":
        return HttpResponseRedirect(reverse('cardDatabase-tournament-decklist'))

    ctx = get_search_form_ctx()
    ctx['basic_form'] = SearchForm()
    ctx['advanced_form'] = AdvancedSearchForm()
    ctx['zones'] = UserDeckListZone.objects.filter(decklist__pk=decklist.pk). \
        order_by('-zone__show_by_default', 'position')
    ctx['decklist_cards'] = DeckListCard.objects.filter(decklist__pk=decklist.pk)
    ctx['decklist'] = decklist
    ctx['deck_formats'] = Format.objects.all()
    return render(request, 'cardDatabase/html/edit_decklist.html', context=ctx)
