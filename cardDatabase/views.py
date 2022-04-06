import json
import re

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.forms.fields import MultipleChoiceField
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib.auth import login as django_login, authenticate, logout as django_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth import login, authenticate
from django.utils.safestring import mark_safe

from .forms import SearchForm, AdvancedSearchForm, AddCardForm, UserRegistrationForm
from .models.DeckList import DeckList, UserDeckListZone, DeckListZone, DeckListCard
from .models.CardType import Card, Race
from fowsim import constants as CONS
from fowsim.decorators import site_admins, desktop_only, logged_out


def get_search_form_ctx():
    try:
        race_values = Race.objects.values('name')
        races_list = list(map(lambda x : x['name'], race_values))  # Remove blank string
        races_list.sort()
        races_list.remove('')
    except Exception:
        races_list = []


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
        if card_type in CONS.SEARCH_CARD_TYPES_INCLUDE:
            for also_included_type in CONS.SEARCH_CARD_TYPES_INCLUDE[card_type]:
                card_type_query |= Q(types__name=also_included_type)
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


def get_attr_query(data, colour_match, colour_combination):
    extra_queries = []
    attr_query = Q()
    attr_annotation = {'colour_combination_count': Count('colours__db_representation')}
    annotation_filter = Q()
    if colour_match == CONS.DATABASE_COLOUR_MATCH_ANY or not colour_match:
        for card_attr in data:
            attr_query |= Q(colours__db_representation=card_attr)

    if colour_match == CONS.DATABASE_COLOUR_MATCH_EXACT:
        for fow_attr, attr_name in CONS.COLOUR_CHOICES:
            if fow_attr not in data:
                attr_query &= ~Q(colours__db_representation=fow_attr)

        annotation_filter &= Q(colour_combination_count=len(data))

    elif colour_match == CONS.DATABASE_COLOUR_MATCH_ALL:
        #  This behaves super weird and I don't understand it so there's just a list of queries to run when searching
        #  by all instead of one large one because it filters everything and seems wrong.
        #  It's inefficient so try avoid using it if possible since it does another db call for each query
        for data_attr in data:
            extra_queries.append(Q(colours__db_representation=data_attr))
        annotation_filter &= Q(colour_combination_count__gte=len(data))

    if colour_combination == CONS.DATABASE_COLOUR_COMBINATION_MONO:
        annotation_filter &= Q(colour_combination_count=1)

    elif colour_combination == CONS.DATABASE_COLOUR_COMBINATION_MULTI:
        annotation_filter &= Q(colour_combination_count__gte=2)

    return attr_query & annotation_filter, attr_annotation, extra_queries


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


def get_keywords_query(data):
    keywords_query = Q()
    for keyword in data:
        keywords_query |= Q(ability_texts__text__icontains=keyword)
    return keywords_query


def get_set_number_sort_value(set_number):
    #  Need to sort them backwards since it gets reversed to show most recent first
    #  Just make them a negative integer of itself (removing characters)
    if set_number:
        num = re.sub('[^0-9]', '', set_number)  # Remove non-numeric
        if num.isnumeric():
            return -1 * int(num)
    return float('-inf')


def sort_cards(cards, sort_by, is_reversed):
    if sort_by == CONS.DATABASE_SORT_BY_MOST_RECENT or not sort_by:
        return sorted(cards, key=lambda item:
                      (CONS.SETS_IN_ORDER.index(item.set_code),
                       get_set_number_sort_value(item.set_number)),
                      reverse=not is_reversed)  # (last set comes first, flip the reversed flag
    elif sort_by == CONS.DATABASE_SORT_BY_TOTAL_COST:
        return sorted(cards, key=lambda item:
                      (item.total_cost,
                       -CONS.SETS_IN_ORDER.index(item.set_code),
                       get_set_number_sort_value(item.set_number)),
                      reverse=is_reversed)
    elif sort_by == CONS.DATABASE_SORT_BY_ALPHABETICAL:
        return sorted(cards, key=lambda item:
                      (item.name,
                       CONS.SETS_IN_ORDER.index(item.set_code),
                       get_set_number_sort_value(item.set_number)),
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

        attr_query, attr_annotation, attr_extra_queries = get_attr_query(
            advanced_form.cleaned_data['colours'], advanced_form.cleaned_data['colour_match'],
            advanced_form.cleaned_data['colour_combination'])
        race_query = get_race_query(advanced_form.cleaned_data['race'])
        set_query = get_set_query(advanced_form.cleaned_data['sets'])
        card_type_query = get_card_type_query(advanced_form.cleaned_data['card_type'])
        rarity_query = get_rarity_query(advanced_form.cleaned_data['rarity'])
        divinity_query = get_divinity_query(advanced_form.cleaned_data['divinity'])
        atk_query = get_atk_def_query(advanced_form.cleaned_data['atk_value'],
                                      advanced_form.cleaned_data['atk_comparator'], 'ATK')
        def_query = get_atk_def_query(advanced_form.cleaned_data['def_value'],
                                      advanced_form.cleaned_data['def_comparator'], 'DEF')
        keywords_query = get_keywords_query(advanced_form.cleaned_data['keywords'])

        cards = (Card.objects.filter(text_query).
                 annotate(**attr_annotation).filter(attr_query).
                 filter(race_query).
                 filter(set_query).
                 filter(card_type_query).
                 filter(rarity_query).
                 filter(divinity_query).
                 filter(atk_query).
                 filter(def_query).
                 filter(keywords_query).
                 exclude(get_unsupported_sets_query()).
                 distinct())

        for q in attr_extra_queries:
            cards = cards.filter(q)
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

    return set_code, None


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
            add_card_form.save_m2m()
            return HttpResponseRedirect(reverse('cardDatabase-view-card', kwargs={'card_id': new_card.card_id}))
        else:
            ctx |= {'add_card_form': add_card_form}
    return render(request, 'cardDatabase/html/add_card.html', context=ctx)


@login_required
@site_admins
def test_error(request):
    return 1 / 0


@login_required
def user_decklists(request):
    ctx = dict()
    ctx['decklists'] = DeckList.objects.filter(profile=request.user.profile).order_by('-last_modified')
    return render(request, 'cardDatabase/html/user_decklists.html', context=ctx)


@login_required
def create_decklist(request):
    decklist = DeckList.objects.create(profile=request.user.profile, name='Untitled Deck')
    for default_zone in DeckListZone.objects.filter(show_by_default=True):
        UserDeckListZone.objects.create(zone=default_zone, position=default_zone.position, decklist=decklist)
    if request.user_agent.is_mobile or request.user_agent.is_tablet:
        return HttpResponseRedirect(reverse('cardDatabase-edit-decklist-mobile', kwargs={'decklist_id': decklist.id}))
    else:
        return HttpResponseRedirect(reverse('cardDatabase-edit-decklist', kwargs={'decklist_id': decklist.id}))

@login_required
@desktop_only
def edit_decklist(request, decklist_id=None):
    # Check that the user matches the decklist
    decklist = get_object_or_404(DeckList, pk=decklist_id, profile__user=request.user)
    ctx = get_search_form_ctx()
    ctx['basic_form'] = SearchForm()
    ctx['advanced_form'] = AdvancedSearchForm()
    ctx['zones'] = UserDeckListZone.objects.filter(decklist__pk=decklist.pk).\
        order_by('-zone__show_by_default', 'position')
    ctx['decklist_cards'] = DeckListCard.objects.filter(decklist__pk=decklist.pk)
    ctx['decklist'] = decklist
    return render(request, 'cardDatabase/html/edit_decklist.html', context=ctx)

@login_required
def edit_decklist_mobile(request, decklist_id=None):
    # Check that the user matches the decklist
    decklist = get_object_or_404(DeckList, pk=decklist_id, profile__user=request.user)
    ctx = get_search_form_ctx()
    ctx['basic_form'] = SearchForm()
    ctx['advanced_form'] = AdvancedSearchForm()
    ctx['zones'] = UserDeckListZone.objects.filter(decklist__pk=decklist.pk).\
        order_by('-zone__show_by_default', 'position')
    ctx['decklist_cards'] = DeckListCard.objects.filter(decklist__pk=decklist.pk)
    ctx['decklist'] = decklist
    return render(request, 'cardDatabase/html/edit_decklist_mobile.html', context=ctx)

@login_required
@require_POST
@desktop_only
def save_decklist(request, decklist_id=None):
    decklist_data = json.loads(request.body.decode('UTF-8'))['decklist_data']

    # Check user matches the decklist
    decklist = get_object_or_404(DeckList, pk=decklist_id, profile__user=request.user)
    decklist.name = decklist_data['name']
    decklist.comments = decklist_data['comments']
    decklist.save()
    #  Remove old cards, then rebuild it
    DeckListCard.objects.filter(decklist__pk=decklist.pk).delete()
    UserDeckListZone.objects.filter(decklist__pk=decklist.pk).delete()
    zone_count = 0
    for zone_data in decklist_data['zones']:
        zone, created = DeckListZone.objects.get_or_create(name=zone_data['name'])
        user_zone, created = UserDeckListZone.objects.get_or_create(zone=zone, position=zone_count, decklist=decklist)
        for card_data in zone_data['cards']:
            card = Card.objects.get(card_id=card_data['id'])
            DeckListCard.objects.get_or_create(
                decklist=decklist,
                card=card,
                position=card_data['position'],
                zone=user_zone,
                quantity=card_data['quantity']
            )
        zone_count += 1

    return HttpResponse('')


def process_decklist_comments(comments):
    output = []
    #  Either "\n" or text in "[[ ]]"
    matches = re.findall('(\[\[.*?\]\])|(\\n)', comments)
    for match in matches:
        match = match[0] or match[1]
        if match == '\n':
            splits = comments.split(match, 1)
            output.append(splits[0])
            output.append(mark_safe('<br />'))
            comments = splits[1]
        else:
            try:
                match = match[2:-2]  # Cut off "[[ ]]"
                card = Card.objects.get(Q(name__iexact=match) | Q(name_without_punctuation__iexact=match))
                view_card_url = reverse('cardDatabase-view-card', kwargs={"card_id": card.card_id})
                # Consume the string split by split so we can mark safe only the sections with imgs to avoid html injection
                splits = comments.split(match, 1)
                output.append(splits[0][:-2])
                output.append(mark_safe(f'<a class="referenced-card" href="{view_card_url}">{card.name}<img class="hover-card-img" src="{card.card_image.url}"/></a>'))
                comments = splits[1][2:]
            except Card.DoesNotExist:
                pass
    else:
        output.append(comments)

    return output


def view_decklist(request, decklist_id):
    decklist = get_object_or_404(DeckList, pk=decklist_id)
    cards = decklist.cards.all()
    zones = UserDeckListZone.objects.filter(decklist=decklist).order_by('position').values_list('zone__name', flat=True).distinct()
    comments = process_decklist_comments(decklist.comments)
    return render(request, 'cardDatabase/html/view_decklist.html', context={'decklist': decklist, 'zones': zones, 'cards': cards, 'comments': comments})


def logout(request):
    django_logout(request)
    return HttpResponseRedirect(reverse('cardDatabase-search'))


def userPreferences(request):
    return HttpResponse('')


@csrf_exempt
@login_required
def delete_decklist(request, decklist_id=None):
    if decklist_id:
        try:
            decklist = DeckList.objects.get(pk=decklist_id)
            if decklist.profile.user == request.user:  # Check they aren't deleting other people's lists
                decklist.delete()
        except DeckList.DoesNotExist:
            pass
    return HttpResponseRedirect(reverse('cardDatabase-user-decklists'))


@logged_out
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect(reverse('cardDatabase-user-decklists'))
    else:
        form = UserRegistrationForm()
    return render(request, 'cardDatabase/html/register.html', {'form': form})


def desktop_only(request):
    return render(request, 'cardDatabase/html/desktop_only.html', {})
