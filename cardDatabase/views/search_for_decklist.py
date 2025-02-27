from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt

from cardDatabase.forms import DecklistSearchForm
from cardDatabase.models import Format
from cardDatabase.views.utils.search_context import get_form_from_params, decklist_search


@csrf_exempt
def get(request):
    ctx = {}
    decklist_form = None
    form_type = request.GET.get('form_type', None)
    if form_type == 'decklist-form':
        decklist_form = get_form_from_params(DecklistSearchForm, request)
        if decklist_form.is_valid():
            ctx['decklist_form_data'] = decklist_form.cleaned_data
        ctx |= {'decklists': decklist_search(decklist_form)}

    ctx['formats'] = Format.objects.all()
    ctx['decklist_form'] = decklist_form or DecklistSearchForm()

    if 'decklists' in ctx:
        paginator = Paginator(ctx['decklists'], request.GET.get('num_per_page', 30))
        page_number = request.GET.get('page', 1)
        ctx['page_range'] = paginator.get_elided_page_range(number=page_number, on_each_side=1, on_ends=1)
        ctx['total_count'] = len(ctx['decklists'])
        ctx['decklists'] = paginator.get_page(page_number)

    return render(request, 'cardDatabase/html/decklist_search.html', context=ctx)
