from django.shortcuts import render
from django.core.paginator import Paginator

from cardDatabase.forms import TournamentFilterForm
from cardDatabase.models import Format
from cardDatabase.views.utils.search_context import get_form_from_params

from cardDatabase.models.Tournament import Tournament, TournamentLevel

def get(request):
    ctx = {}
    tournament_form = None
    form_type = request.GET.get('form_type', None)
    if form_type == 'tournament-form':
        tournament_form = get_form_from_params(TournamentFilterForm, request)
        if tournament_form.is_valid():
            ctx['tournament_form_data'] = tournament_form.cleaned_data
        ctx |= {'tournaments': tournament_search(tournament_form)}

    ctx['tournament_levels'] = TournamentLevel.objects.all()
    ctx['formats'] = Format.objects.all()
    ctx['tournament_form'] = tournament_form or TournamentFilterForm()

    if 'tournaments' in ctx:
        paginator = Paginator(ctx['tournaments'], request.GET.get('num_per_page', 30))
        page_number = request.GET.get('page', 1)
        ctx['page_range'] = paginator.get_elided_page_range(number=page_number, on_each_side=1, on_ends=1)
        ctx['total_count'] = len(ctx['tournaments'])
        ctx['tournaments'] = paginator.get_page(page_number)

    tournaments = Tournament.objects.order_by('-start_datetime').all()

    return render(request, 'tournament/tournament_list.html', context=ctx)

def tournament_search(tournament_form):
    decklists = []
    if tournament_form.is_valid():
        search_text = tournament_form.cleaned_data['contains_card']
        text_exactness = tournament_form.cleaned_data['text_exactness']
        deck_format_filter = get_deck_format_query(tournament_form.cleaned_data['deck_format'])
        decklists = DeckList.objects.exclude(get_unsupported_decklists_query()).distinct()
        decklists = decklists.filter(deck_format_filter)
        decklists = apply_deckcard_cardname_search(decklists, search_text, ['name'], text_exactness)
        decklists = decklists.order_by('-last_modified')

    return decklists