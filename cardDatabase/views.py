from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from .forms import SearchForm
from .models.CardType import Card


def search(request):
    ctx = {}
    if request.method == 'GET':
        form = SearchForm()

    elif request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            # Filter cards and show them
            search_text = form.cleaned_data['generic_text']
            ctx['cards'] = Card.objects.filter(Q(name__icontains=search_text) |
                                               Q(ability_texts__text__icontains=search_text))

    ctx['form'] = form
    return render(request, 'cardDatabase/html/search.html', context=ctx)


def view_card(request, card_id=None):
    card = get_object_or_404(Card, card_id=card_id)
    return render(request, 'cardDatabase/html/view_card.html', context={'card': card, 'form': SearchForm()})
