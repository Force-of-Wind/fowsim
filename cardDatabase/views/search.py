from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.core.paginator import Paginator

from cardDatabase.forms import SearchForm, AdvancedSearchForm
from cardDatabase.views.utils.search_context import *


@csrf_exempt
def get(request):
    ctx = get_search_form_ctx()
    basic_form = None
    advanced_form = None
    spoilers = request.GET.get('spoiler_season', None)
    if spoilers:
        set_codes = spoilers.split(',')
        ctx['cards'] = Card.objects.filter(get_set_query(set_codes)).order_by('-pk')
    else:
        form_type = request.GET.get('form_type', None)
        if form_type == 'basic-form':
            basic_form = get_form_from_params(SearchForm, request)
            ctx |= basic_search(basic_form)
        elif form_type == 'advanced-form':
            advanced_form = get_form_from_params(AdvancedSearchForm, request)
            ctx |= advanced_search(advanced_form)

    ctx['basic_form'] = basic_form or SearchForm()
    ctx['advanced_form'] = advanced_form or AdvancedSearchForm()

    if 'cards' in ctx:
        paginator = Paginator(ctx['cards'], request.GET.get('num_per_page', 30))
        page_number = request.GET.get('page', 1)
        ctx['page_range'] = paginator.get_elided_page_range(number=page_number, on_each_side=1, on_ends=1)
        ctx['total_count'] = len(ctx['cards'])
        ctx['cards'] = paginator.get_page(page_number)
    return render(request, 'cardDatabase/html/search.html', context=ctx)
