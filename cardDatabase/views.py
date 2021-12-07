from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.forms.fields import MultipleChoiceField
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import SearchForm, AdvancedSearchForm, AddCardForm
from .models.CardType import Card, Race
from fowsim import constants as CONS
from fowsim.decorators import site_admins


def get_search_form_ctx():
    race_values = Race.objects.values('name')
    races_list = list(map(lambda x : x['name'], race_values))  # Remove blank string
    races_list.sort()
    races_list.remove('')

    return {
        'races_list': list(races_list),
        'card_types_list': CONS.DATABASE_CARD_TYPE_GROUPS,
        'sets_json': CONS.SET_DATA
    }

def get_race_query(data):
    race_query = Q()
    for race in data:
        race_query |= Q(races__name=race)
    return race_query

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
        if fow_set in CONS.SEARCH_SETS_INCLUDE:
            #  Search implies more than just itself, e.g. AO3 includes AO3 Buy a Box, so that those sets too
            for also_included_set in CONS.SEARCH_SETS_INCLUDE[fow_set]:
                # No trailing '-' because the '-' is included in CONS
                set_query |= Q(card_id__istartswith=also_included_set)
        set_query |= Q(card_id__istartswith=fow_set + '-')
    return set_query


def get_attr_query(data):
    attr_query = Q()
    for card_attr in data:
        attr_query |= Q(colours__db_representation=card_attr)
    return attr_query


def separate_text_query(field, search_text, exactness_option):
    """
    :param field: name of the field to search e.g. 'name' or 'ability_text'
    :param search_text: actual string to query for
    :param exactness_option: which option was selected in constants.py:TEXT_EXACTNESS_OPTIONS
    :return: query object using the chosen setting
    """
    q = Q()
    if search_text and field:
        if exactness_option == CONS.TEXT_EXACT:
            # Simply check that the whole phrase exists without edits
            return Q(**{field + '__icontains': search_text})
        else:  # Either "Contains all" or 'Contains at least one"
            '''
            Check for each individual word, not the whole phrase
            E.g. Contains "Lumia fated rebirth"
            becomes Contains "Lumia" and/or contains "fated" and/or contains "rebirth"
            '''
            for word in search_text.split(' '):
                word_query = Q(**{field + '__icontains': word})
                if exactness_option == CONS.TEXT_CONTAINS_ALL:
                    q &= word_query
                elif exactness_option == CONS.TEXT_CONTAINS_AT_LEAST_ONE:
                    q |= word_query
    return q


def get_text_query(search_text, text_search_fields, exactness_option):
    text_query = Q()
    if search_text:
        for field in text_search_fields:
            #  Value of the field is the destination to search e.g. 'name' or 'ability_text
            text_query |= separate_text_query(field, search_text, exactness_option)
            if field == 'name':
                # Also check the alternative name
                text_query |= separate_text_query('name_without_punctuation', search_text, exactness_option)

    return text_query


def get_divinity_query(data):
    divinity_query = Q()
    for div in data:
        divinity_query |= Q(divinity=div)
    return divinity_query


def get_atk_def_query(value, comparator, field_name):
    if value is not None and comparator:
        return Q(**{f'{field_name}__{comparator}': value})
    return Q()


def sort_cards(cards, sort_by, is_reversed):
    if sort_by == CONS.DATABASE_SORT_BY_MOST_RECENT or not sort_by:
        return sorted(cards, key=lambda item:
                      (CONS.SETS_IN_ORDER.index(item.set_code),
                       item.set_number),
                      reverse=not is_reversed)  # (last set comes first, flip the reversed flag
    elif sort_by == CONS.DATABASE_SORT_BY_TOTAL_COST:
        return sorted(cards, key=lambda item:
                      (item.total_cost,
                       CONS.SETS_IN_ORDER.index(item.set_code),
                       item.set_number),
                      reverse=is_reversed)
    elif sort_by == CONS.DATABASE_SORT_BY_ALPHABETICAL:
        return sorted(cards, key=lambda item:
                      (item.name,
                       CONS.SETS_IN_ORDER.index(item.set_code),
                       item.set_number),
                      reverse=is_reversed)
    raise Exception('Attempting to sort card by invalid selection')


def get_unsupported_sets_query():
    unsupported_sets = Q()
    for unsupported_set in CONS.UNSEARCHED_DATABASE_SETS:
        unsupported_sets |= Q(card_id__istartswith=unsupported_set)

    return unsupported_sets


def basic_search(basic_form):
    cards = []
    if basic_form.is_valid():
        search_text = basic_form.cleaned_data['generic_text']
        text_query = get_text_query(search_text, ['name', 'name_without_punctuation', 'ability_texts__text', 'races__name'], CONS.TEXT_CONTAINS_ALL)
        cards = Card.objects.filter(text_query).exclude(get_unsupported_sets_query()).distinct()
        cards = sort_cards(cards, CONS.DATABASE_SORT_BY_MOST_RECENT, False)
    return {'cards': cards}


def advanced_search(advanced_form):
    ctx = {}
    cards = []
    if advanced_form.is_valid():
        ctx['advanced_form_data'] = advanced_form.cleaned_data
        text_query = get_text_query(advanced_form.cleaned_data['generic_text'],
                                    advanced_form.cleaned_data['text_search_fields'],
                                    advanced_form.cleaned_data['text_exactness'])

        attr_query = get_attr_query(advanced_form.cleaned_data['colours'])
        race_query = get_race_query(advanced_form.cleaned_data['race'])
        set_query = get_set_query(advanced_form.cleaned_data['sets'])
        card_type_query = get_card_type_query(advanced_form.cleaned_data['card_type'])
        rarity_query = get_rarity_query(advanced_form.cleaned_data['rarity'])
        divinity_query = get_divinity_query(advanced_form.cleaned_data['divinity'])
        atk_query = get_atk_def_query(advanced_form.cleaned_data['atk_value'],
                                      advanced_form.cleaned_data['atk_comparator'], 'ATK')
        def_query = get_atk_def_query(advanced_form.cleaned_data['def_value'],
                                      advanced_form.cleaned_data['def_comparator'], 'DEF')

        cards = (Card.objects.filter(text_query).
                 filter(attr_query).
                 filter(race_query).
                 filter(set_query).
                 filter(card_type_query).
                 filter(rarity_query).
                 filter(divinity_query).
                 filter(atk_query).
                 filter(def_query).
                 exclude(get_unsupported_sets_query()).
                 distinct())
        cards = sort_cards(cards, advanced_form.cleaned_data['sort_by'],
                           advanced_form.cleaned_data['reverse_sort'] or False)
        cost_filters = advanced_form.cleaned_data['cost']
        if len(cost_filters) > 0:
            # Don't need DB query to do total cost, remove all that don't match if any were chosen
            if 'X' in cost_filters:
                cards = [x for x in cards
                         if str(x.total_cost) in cost_filters
                         or x.cost and '{X}' in x.cost]
            else:
                cards = [x for x in cards if str(x.total_cost) in cost_filters]
    return ctx | {'cards': cards}


def get_form_from_params(form_class, request):
    # Grab what query params from request.GET match the expected form values and put them into the dictionary input_data
    # Then instantiate the form using those values
    input_data = {}
    for form_field_name in form_class.__dict__['declared_fields']:
        if type(form_class.__dict__['declared_fields'][form_field_name]) == MultipleChoiceField:
            query_param_value = request.GET.getlist(form_field_name, None)
        else:
            query_param_value = request.GET.get(form_field_name, None)
        if query_param_value:
            input_data[form_field_name] = query_param_value
    return form_class(input_data)


@csrf_exempt
def search_for_cards(request):
    ctx = get_search_form_ctx()
    basic_form = None
    advanced_form = None
    form_type = request.GET.get('form_type', None)
    if form_type == 'basic-form':
        basic_form = get_form_from_params(SearchForm, request)
        ctx = ctx | basic_search(basic_form)
    elif form_type == 'advanced-form':
        advanced_form = get_form_from_params(AdvancedSearchForm, request)
        ctx = ctx | advanced_search(advanced_form)

    ctx['basic_form'] = basic_form or SearchForm()
    ctx['advanced_form'] = advanced_form or AdvancedSearchForm()
    if 'cards' in ctx:
        paginator = Paginator(ctx['cards'], request.GET.get('num_per_page', 30))
        page_number = request.GET.get('page', 1)
        ctx['page_range'] = paginator.get_elided_page_range(number=page_number)
        ctx['total_count'] = len(ctx['cards'])
        ctx['cards'] = paginator.get_page(page_number)
    return render(request, 'cardDatabase/html/search.html', context=ctx)


def full_set_code_to_name(set_code):
    for cluster in CONS.SET_DATA['clusters']:
        for fow_set in cluster['sets']:
            if fow_set['code'] == set_code:
                return fow_set['name']


def searchable_set_and_name(set_code):
    #  Check CONS.SET_DATA first, not all sets are in there, some are extra things like 'Buy a Box'
    #  which should be included in CONS.SEARCH_SETS_INCLUDE
    to_return = full_set_code_to_name(set_code)
    if to_return:
        return set_code, to_return

    #  Search for "parent" set, e.g. "AO2 Buy a Box" becomes "AO2"
    for fow_set in CONS.SEARCH_SETS_INCLUDE:
        if set_code in CONS.SEARCH_SETS_INCLUDE[fow_set]:
            return fow_set, full_set_code_to_name(fow_set)


def view_card(request, card_id=None):
    card = get_object_or_404(Card, card_id=card_id)
    referred_by = Card.objects.filter(ability_texts__text__contains=f'"{card.name}"')
    ctx = get_search_form_ctx()
    ctx['card'] = card
    ctx['referred_by'] = referred_by
    ctx['basic_form'] = SearchForm()
    ctx['advanced_form'] = AdvancedSearchForm()
    set_code, set_name = searchable_set_and_name(card.set_code)
    ctx['set_name'] = set_name
    ctx['set_code'] = set_code

    return render(request, 'cardDatabase/html/view_card.html', context=ctx)


@login_required
@site_admins
def add_card(request):
    ctx = {}
    if request.method == 'GET':
        ctx |= {'add_card_form': AddCardForm()}
    elif request.method == 'POST':
        add_card_form = AddCardForm(request.POST, request.FILES)
        if add_card_form.is_valid():
            new_card = add_card_form.save()
            return HttpResponseRedirect(reverse('cardDatabase-view-card', kwargs={'card_id': new_card.card_id}))
        else:
            ctx |= {'add_card_form': add_card_form}
    return render(request, 'cardDatabase/html/add_card.html', context=ctx)
