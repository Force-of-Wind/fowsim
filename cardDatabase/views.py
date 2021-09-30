from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from .forms import SearchForm, AdvancedSearchForm
from .models.CardType import Card


def search(request):
    ctx = {}
    if request.method == 'GET':
        basic_form = SearchForm()
        advanced_form = AdvancedSearchForm()

    elif request.method == 'POST':
        if 'basic-form' in request.POST:
            basic_form = SearchForm(request.POST)
            advanced_form = AdvancedSearchForm()
            if basic_form.is_valid():
                # Filter cards and show them
                search_text = basic_form.cleaned_data['generic_text']
                #TODO Sort by something useful, dont assume id
                ctx['cards'] = Card.objects.filter(Q(name__icontains=search_text) | Q(ability_texts__text__icontains=search_text))\
                    .distinct().order_by('-id')
        elif 'advanced-form' in request.POST:
            basic_form = SearchForm()
            advanced_form = AdvancedSearchForm(request.POST)
            if advanced_form.is_valid():
                ctx['cards'] = Card.objects.get(name='Otherworld Dreams')


    ctx['basic_form'] = basic_form
    ctx['advanced_form'] = advanced_form
    return render(request, 'cardDatabase/html/search.html', context=ctx)


def view_card(request, card_id=None):
    card = get_object_or_404(Card, card_id=card_id)
    return render(request, 'cardDatabase/html/view_card.html', context={'card': card, 'form': SearchForm()})
