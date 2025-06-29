from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from cardDatabase.forms import AddCardForm
from fowsim.decorators import site_admins
from cardDatabase.views.utils.search_context import get_set_query

from cardDatabase.models.CardType import Card
from cardDatabase.models.Spoilers import SpoilerSeason

@login_required
@site_admins
def get(request):
    ctx = {}
    if request.method == 'GET':
        ctx |= {'add_card_form': AddCardForm(), 'added_ids': []}

        spoiler_sets = list(SpoilerSeason.objects.filter(is_active=True).values_list('set_code', flat=True))
        if len(spoiler_sets):
            set_query = get_set_query(spoiler_sets)
            ctx |= {'added_ids': list(Card.objects.filter(set_query).values_list('card_id', flat=True).distinct())}
    elif request.method == 'POST':
        add_card_form = AddCardForm(request.POST, request.FILES)
        if add_card_form.is_valid():
            new_card = add_card_form.save()
            add_card_form.save_m2m()
            return HttpResponseRedirect(reverse('cardDatabase-view-card', kwargs={'card_id': new_card.card_id}))
        else:
            ctx |= {'add_card_form': add_card_form}
    return render(request, 'cardDatabase/html/add_card.html', context=ctx)