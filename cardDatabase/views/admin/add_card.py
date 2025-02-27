from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from cardDatabase.forms import AddCardForm
from fowsim.decorators import site_admins


@login_required
@site_admins
def get(request):
    ctx = {}
    if request.method == 'GET':
        ctx |= {'add_card_form': AddCardForm()}
    elif request.method == 'POST':
        add_card_form = AddCardForm(request.POST, request.FILES)
        if add_card_form.is_valid():
            new_card = add_card_form.save()
            add_card_form.save_m2m()
            return HttpResponseRedirect(reverse('cardDatabase-view-card', kwargs={'card_id': new_card.card_id}))
        else:
            ctx |= {'add_card_form': add_card_form}
    return render(request, 'cardDatabase/html/add_card.html', context=ctx)
