import re
import json

from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from .forms import SearchForm, AdvancedSearchForm
from .models.CardType import Card
from fowsim import constants as CONS


def get_search_form_ctx():
    return {
        'card_types_list': CONS.DATABASE_CARD_TYPE_GROUPS,
        'sets_json': CONS.SET_DATA
    }


def search(request):
    ctx = get_search_form_ctx()
    if request.method == 'GET':
        basic_form = SearchForm()
        advanced_form = AdvancedSearchForm()

    elif request.method == 'POST':
        unsupported_sets = Q()
        for unsupported_set in CONS.UNSUPPORTED_DATABASE_SETS:
            unsupported_sets |= Q(card_id__istartswith=unsupported_set + '-')

        if 'basic-form' in request.POST:
            basic_form = SearchForm(request.POST)
            advanced_form = AdvancedSearchForm()
            if basic_form.is_valid():
                # Filter cards and show them
                search_text = basic_form.cleaned_data['generic_text']
                #TODO Sort by something useful, dont assume id
                ctx['cards'] = Card.objects.filter(Q(name__icontains=search_text) | Q(ability_texts__text__icontains=search_text)
                                                   | Q(races__name__icontains=search_text)).exclude(unsupported_sets).distinct().order_by('-id')
        elif 'advanced-form' in request.POST:
            basic_form = SearchForm()
            advanced_form = AdvancedSearchForm(request.POST)
            if advanced_form.is_valid():
                ctx['advanced_form_data'] = advanced_form.cleaned_data
                search_text = advanced_form.cleaned_data['generic_text']

                text_query = Q()
                if search_text:
                    text_search_fields = advanced_form.cleaned_data['text_search_fields']
                    for field in text_search_fields:
                        #  Value of the field is the destination to search e.g. 'name' or 'ability_text
                        text_query |= Q(**{field + '__icontains': search_text})

                attr_query = Q()
                for card_attr in advanced_form.cleaned_data['colours']:
                    if card_attr == CONS.ATTRIBUTE_VOID_CODE:
                        void_query = Q()
                        # Build query to exclude cards with any attribute in the cost e.g. not 'R' and not 'G' etc.
                        for attr_code in CONS.ATTRIBUTE_CODES:
                            void_query &= ~Q(cost__contains=attr_code)
                        attr_query |= void_query
                    else:
                        attr_query |= Q(cost__contains=card_attr)

                set_query = Q()
                for fow_set in advanced_form.cleaned_data['sets']:
                    set_query |= Q(card_id__istartswith=fow_set + '-')

                card_type_query = Q()
                for card_type in advanced_form.cleaned_data['card_type']:
                    card_type_query |= Q(types__name=card_type)

                rarity_query = Q()
                for rarity in advanced_form.cleaned_data['rarity']:
                    rarity_query |= Q(rarity=rarity)
                # TODO fix ordering
                ctx['cards'] = (Card.objects.filter(text_query).
                                filter(attr_query).
                                filter(set_query).
                                filter(card_type_query).
                                filter(rarity_query).
                                exclude(unsupported_sets).
                                distinct().
                                order_by('-id')
                                )
                cost_filters = advanced_form.cleaned_data['cost']
                if len(cost_filters) > 0:
                    # Don't need DB query to do total cost, remove all that don't match if any were chosen
                    # TODO
                    if 'X' in cost_filters:
                        ctx['cards'] = [x for x in ctx['cards']
                                        if str(x.total_cost) in cost_filters
                                        or '{X}' in x.cost]
                    else:
                        ctx['cards'] = [x for x in ctx['cards'] if str(x.total_cost) in cost_filters]

    ctx['basic_form'] = basic_form
    ctx['advanced_form'] = advanced_form
    return render(request, 'cardDatabase/html/search.html', context=ctx)


def view_card(request, card_id=None):
    card = get_object_or_404(Card, card_id=card_id)
    referred_by = Card.objects.filter(ability_texts__text__contains=f'"{card.name}"')
    ctx = get_search_form_ctx()
    ctx['card'] = card
    ctx['referred_by'] = referred_by
    ctx['basic_form'] = SearchForm()
    ctx['advanced_form'] = AdvancedSearchForm()

    return render(request, 'cardDatabase/html/view_card.html', context=ctx)
