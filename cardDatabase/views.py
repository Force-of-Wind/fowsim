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


def get_rarity_query(data):
    rarity_query = Q()
    for rarity in data:
        rarity_query |= Q(rarity=rarity)
    return rarity_query


def get_card_type_query(data):
    card_type_query = Q()
    for card_type in data:
        card_type_query |= Q(types__name=card_type)
    return card_type_query


def get_set_query(data):
    set_query = Q()
    for fow_set in data:
        set_query |= Q(card_id__istartswith=fow_set + '-')
    return set_query


def get_attr_query(data):
    attr_query = Q()
    for card_attr in data:
        if card_attr == CONS.ATTRIBUTE_VOID_CODE:
            void_query = Q()
            # Build query to exclude cards with any attribute in the cost e.g. not 'R' and not 'G' etc.
            for attr_code in CONS.ATTRIBUTE_CODES:
                void_query &= ~Q(cost__contains=attr_code)
            attr_query |= void_query
        else:
            attr_query |= Q(cost__contains=card_attr)
    return attr_query


def get_text_query(search_text, text_search_fields):
    text_query = Q()
    if search_text:
        for field in text_search_fields:
            #  Value of the field is the destination to search e.g. 'name' or 'ability_text
            text_query |= Q(**{field + '__icontains': search_text})
            if field == 'name':
                # Also check the alternative name
                text_query |= Q(**{'name_without_punctuation__icontains': search_text})

    return text_query


def get_divinity_query(data):
    divinity_query = Q()
    for div in data:
        divinity_query |= Q(divinity=div)
    return divinity_query


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
                ctx['cards'] = Card.objects.filter(Q(name__icontains=search_text) |
                                                   Q(name_without_punctuation__icontains=search_text) |
                                                   Q(ability_texts__text__icontains=search_text) |
                                                   Q(races__name__icontains=search_text)
                ).exclude(unsupported_sets).distinct().order_by('-id')
        elif 'advanced-form' in request.POST:
            basic_form = SearchForm()
            advanced_form = AdvancedSearchForm(request.POST)
            if advanced_form.is_valid():
                ctx['advanced_form_data'] = advanced_form.cleaned_data
                text_query = get_text_query(advanced_form.cleaned_data['generic_text'],
                                            advanced_form.cleaned_data['text_search_fields'])

                attr_query = get_attr_query(advanced_form.cleaned_data['colours'])
                set_query = get_set_query(advanced_form.cleaned_data['sets'])
                card_type_query = get_card_type_query(advanced_form.cleaned_data['card_type'])
                rarity_query = get_rarity_query(advanced_form.cleaned_data['rarity'])
                divinity_query = get_divinity_query(advanced_form.cleaned_data['divinity'])

                # TODO fix ordering
                ctx['cards'] = (Card.objects.filter(text_query).
                                filter(attr_query).
                                filter(set_query).
                                filter(card_type_query).
                                filter(rarity_query).
                                filter(divinity_query).
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
