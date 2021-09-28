from django.shortcuts import render
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
            ctx['cards'] = Card.objects.filter(name__icontains=search_text)

    ctx['form'] = form
    return render(request, 'cardDatabase/html/search.html', context=ctx)


