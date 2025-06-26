from django.shortcuts import render

from cardDatabase.forms import AdvancedSearchForm, SearchForm
from cardDatabase.views.utils.search_context import get_search_form_ctx


def get(request):
    ctx = get_search_form_ctx()
    ctx['basic_form'] = SearchForm()
    ctx['advanced_form'] = AdvancedSearchForm()
    return render(request, 'cardDatabase/html/start.html', context=ctx)