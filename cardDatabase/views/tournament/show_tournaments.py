from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q

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
    else:
        ctx = {'tournaments': tournament_search(None)}

    ctx['tournament_levels'] = TournamentLevel.objects.all()
    ctx['formats'] = Format.objects.all()
    ctx['tournament_form'] = tournament_form or TournamentFilterForm()

    if 'tournaments' in ctx:
        paginator = Paginator(ctx['tournaments'], request.GET.get('num_per_page', 30))
        page_number = request.GET.get('page', 1)
        ctx['page_range'] = paginator.get_elided_page_range(number=page_number, on_each_side=1, on_ends=1)
        ctx['total_count'] = len(ctx['tournaments'])
        ctx['tournaments'] = paginator.get_page(page_number)

    return render(request, 'tournament/tournament_list.html', context=ctx)

def tournament_search(tournament_form):
    tournaments = []
    if tournament_form is not None and tournament_form.is_valid():
        tournaments_query = Q()
        
        if 'tournament_format' in tournament_form.cleaned_data and tournament_form.cleaned_data['tournament_format']:
            tournaments_query &= Q(format__name=tournament_form.cleaned_data['tournament_format'])
        
        if 'tournament_level' in tournament_form.cleaned_data and tournament_form.cleaned_data['tournament_level']:
            tournaments_query &= Q(level__title=tournament_form.cleaned_data['tournament_level'])

        if 'tournament_phase' in tournament_form.cleaned_data and tournament_form.cleaned_data['tournament_phase']:
            tournaments_query &= Q(phase=tournament_form.cleaned_data['tournament_phase'])
        tournaments = Tournament.objects.distinct()
        tournaments = tournaments.filter(tournaments_query)
        tournaments = tournaments.order_by('-start_datetime')
    elif tournament_form is None:
        tournaments = Tournament.objects.distinct()
        tournaments = tournaments.order_by('-start_datetime')

    return tournaments