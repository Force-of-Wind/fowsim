from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from cardDatabase.forms import SearchForm, AdvancedSearchForm
from cardDatabase.models import Format, DeckList
from cardDatabase.models.DeckList import UserDeckListZone, DeckListCard
from cardDatabase.views.utils.search_context import get_search_form_ctx
from fowsim.decorators import mobile_only


@login_required
@mobile_only
def get(request, decklist_id=None):
    # Check that the user matches the decklist
    decklist = get_object_or_404(DeckList, pk=decklist_id, profile__user=request.user)
    ctx = get_search_form_ctx()
    ctx['basic_form'] = SearchForm()
    ctx['advanced_form'] = AdvancedSearchForm()
    ctx['zones'] = UserDeckListZone.objects.filter(decklist__pk=decklist.pk). \
        order_by('-zone__show_by_default', 'position')
    ctx['decklist_cards'] = DeckListCard.objects.filter(decklist__pk=decklist.pk)
    ctx['decklist'] = decklist
    ctx['deck_formats'] = Format.objects.all()
    return render(request, 'cardDatabase/html/edit_decklist_mobile.html', context=ctx)
