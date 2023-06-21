import json
import re
import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.forms.fields import MultipleChoiceField
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404
from django.urls import reverse
from django.contrib.auth import login, authenticate

from .forms import SearchForm, AdvancedSearchForm, AddCardForm, UserRegistrationForm
from .models.DeckList import DeckList, UserDeckListZone, DeckListZone, DeckListCard
from .models.CardType import Card, Race
from .models.Banlist import BannedCard, CombinationBannedCards
from .models.Metrics import PickPeriod, MostPickedCardPickRate, AttributePickRate, CardTotalCostPickRate, CardTypePickRate
from fowsim import constants as CONS
from fowsim.decorators import site_admins, desktop_only, logged_out, mobile_only, reddit_bot


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
    attr_exclusions = Q()
    attr_annotation = {'colour_combination_count': Count('colours__db_representation', distinct=True)}
    annotation_filter = Q()
    if colour_match == CONS.DATABASE_COLOUR_MATCH_ANY or not colour_match:
        for card_attr in data:
            attr_query |= Q(colours__db_representation=card_attr)

    elif colour_match == CONS.DATABASE_COLOUR_MATCH_EXACT:
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

    elif colour_match == CONS.DATABASE_COLOUR_MATCH_ONLY:
        for colour_code, colour_name in CONS.COLOUR_CHOICES:
            if colour_code not in data:
                attr_exclusions |= Q(colours__db_representation=colour_code)

    if colour_combination == CONS.DATABASE_COLOUR_COMBINATION_MONO:
        annotation_filter &= Q(colour_combination_count=1)

    elif colour_combination == CONS.DATABASE_COLOUR_COMBINATION_MULTI:
        annotation_filter &= Q(colour_combination_count__gte=2)

    return attr_query & annotation_filter, attr_annotation, extra_queries, attr_exclusions


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
        cards = Card.objects.exclude(get_unsupported_sets_query()).distinct()
        cards = apply_text_search(cards, search_text, ['name', 'ability_texts__text'], CONS.TEXT_CONTAINS_ALL)
        cards = sort_cards(cards, CONS.DATABASE_SORT_BY_MOST_RECENT, False)
    return {'cards': cards}


def field_has_text(text, search_field, card):
    if '__' in search_field:
        splits = search_field.split('__')
        vals = getattr(card, splits[0]).all().values_list(splits[1], flat=True)
        for val in vals:
            if text.casefold() in val.casefold():
                return True

    else:
        val = getattr(card, search_field)
        if text.casefold() in val.casefold():
            return True
    return False


def apply_text_search(cards, text, search_fields, exactness_option):
    if not text:
        return cards

    output = []
    words = text.split(' ')
    if 'name' in search_fields:
        search_fields.append('name_without_punctuation')

    if exactness_option == CONS.TEXT_CONTAINS_AT_LEAST_ONE:
        q = Q()
        for word in words:
            word_query = Q()
            for search_field in search_fields:
                word_query |= Q(**{search_field + '__icontains': word})
            q |= word_query
        output = cards.filter(q)

    elif exactness_option == CONS.TEXT_CONTAINS_ALL:
        # Use db because there's not many terms and this is more efficient
        output = cards
        for word in words:
            word_query = Q()
            for search_field in search_fields:
                word_query |= Q(**{search_field + '__icontains': word})

            output = output.filter(word_query)

    elif exactness_option == CONS.TEXT_EXACT:
        q = Q()
        for search_field in search_fields:
            q |= Q(**{search_field + '__icontains': text})

        output = cards.filter(q)

    return output


def advanced_search(advanced_form):
    ctx = {}
    cards = []
    if advanced_form.is_valid():
        ctx['advanced_form_data'] = advanced_form.cleaned_data

        attr_query, attr_annotation, attr_extra_queries, attr_exclusions = get_attr_query(
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

        cards = (Card.objects.
                 annotate(**attr_annotation).filter(attr_query).exclude(attr_exclusions).
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

        cards = apply_text_search(cards, advanced_form.cleaned_data['generic_text'],
                                  advanced_form.cleaned_data['text_search_fields'],
                                  advanced_form.cleaned_data['text_exactness'])

        cost_filters = advanced_form.cleaned_data['cost']
        if len(cost_filters) > 0:
            # Don't need DB query to do total cost, remove all that don't match if any were chosen
            if 'X' in cost_filters:
                cards = [x for x in cards
                         if str(x.total_cost) in cost_filters
                         or x.cost and '{X}' in x.cost]
            else:
                cards = [x for x in cards if str(x.total_cost) in cost_filters]

        cards = sort_cards(cards, advanced_form.cleaned_data['sort_by'],
                           advanced_form.cleaned_data['reverse_sort'] or False)
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
    spoilers = request.GET.get('spoiler_season', None)
    if spoilers:
        set_codes = spoilers.split(',')
        ctx['cards'] = Card.objects.filter(get_set_query(set_codes)).order_by('-pk')
    else:
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
        ctx['page_range'] = paginator.get_elided_page_range(number=page_number, on_each_side=1, on_ends=1)
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

    prev_card, next_card = get_next_prev_cards(card_id, set_code)
    ctx['prev_card'] = prev_card
    ctx['next_card'] = next_card

    one_month_ago = datetime.datetime.now() - datetime.timedelta(days=30)
    ctx['recent_decklists'] = DeckList.objects.filter(public=True, cards__card__in=([card] + list(card.other_sides)),
                                                      last_modified__gt=one_month_ago).distinct().order_by('-last_modified')
    if not ctx['recent_decklists'].count():
        # There are no recent ones, just grab the up to the 4 most recent ones instead
        ctx['recent_decklists'] = DeckList.objects.filter(public=True, cards__card__in=([card] + list(card.other_sides))).distinct().order_by('-last_modified')[:4]

    return render(request, 'cardDatabase/html/view_card.html', context=ctx)


def get_next_prev_cards(card_id, set_code):
    # get card number from card_id
    try:
        card_id_int = card_id.split("-")[1]
    except IndexError:
        # Unusual set code like 'H2 Buy a Box'
        return None, None

    # if card_id is a dual-sided card, just take the integer part (3 digits)
    if len(card_id_int) > 3:
        card_id_int = card_id_int[:3]

    # get prev and next cards from set_next_card_id method
    try:
        prev_card = set_next_card_id(int(card_id_int), -1, set_code, fill_zeroes=3)
        next_card = set_next_card_id(int(card_id_int), 1, set_code, fill_zeroes=3)
    except ValueError: # Other unusual set codes like NWE-SEC4
        return None, None
    return prev_card, next_card


# method accepts card id as an int, offset to increment/decrement card id value, current set code and how many
# zeroes the final card should fill up to (this is always 3 for the main set card ids, but different for promos)


def set_next_card_id(card_int, offset, set_code, fill_zeroes=None):
    # create either the next/prev card id
    current_card_id = card_int + offset
    current_card_id = set_code + "-" + str(current_card_id).zfill(fill_zeroes)

    # if the next/prev card id doesn't exist, means we are trying to find a card id that isn't in any set,
    # so need to set the set code to the next/prev set if they exist
    if not Card.objects.filter(card_id=current_card_id).exists():
        index = 0
        for current_set in CONS.SET_CHOICES:
            # if current_set[0] equal to our set_code
            if current_set[0] == set_code:
                # decrement/increment index to get next set code
                next_index = index - offset
                # as long as next_index not length of list, or 0, we can set it
                if not next_index >= len(CONS.SET_CHOICES) and not next_index == 0:
                    new_set_code = CONS.SET_CHOICES[next_index][0]
                    break
            # else increment/decrement index to check the next set
            index += 1

        # check that new_set_code has been set, otherwise immediately return '', if new_set_code not set, it means we
        # have reached the beginning or end of all cards in our card database
        if new_set_code:
            # if we are setting the previous card (i.e. previous set), offset will be -1
            if offset < 0:
                # put new_set_code (string) into an array
                set_code_arr = new_set_code.split()

                # get all cards in the new set, the [0]th element card will be the LAST card in this set
                all_cards_in_new_set = Card.objects.filter(get_set_query(set_code_arr)).order_by('-pk')

                # set new card id to the last card's card id, in the PREVIOUS set
                new_card_id = all_cards_in_new_set[0].card_id
            else:
                # set new card id to the NEXT set (where we start from the 1st card, XXX-001
                new_card_id = new_set_code + "-001"

            if Card.objects.filter(card_id=new_card_id).exists():
                return get_object_or_404(Card, card_id=new_card_id)
            else:
                # card id/card that doesn't exist
                return None
        else:  # no new_set_code
            return None

    else:
        # reaching here means our current_card_id exists, so return it
        # if Card.objects.filter(card_id=current_card_id).exists():
        return get_object_or_404(Card, card_id=current_card_id)
        # else:
        #     return ''


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
def deprecated_decklist_url(request):
    return HttpResponseRedirect(reverse('cardDatabase-view-users-decklist', kwargs={'username': request.user.username}))


def view_users_public(request, username=None):
    if username is not None:
        ctx = dict()
        try:
            if request.user.username == username:
                #  Dont filter by is_public
                ctx['decklists'] = DeckList.objects.filter(profile=request.user.profile).order_by('-last_modified')
                ctx['is_owner'] = True
            else:
                ctx['decklists'] = DeckList.objects.filter(
                    profile=User.objects.get(username=username).profile, public=True).order_by('-last_modified')
                ctx['is_owner'] = False
        except User.DoesNotExist:
            raise Http404
            
        return render(request, 'cardDatabase/html/user_decklists.html', context=ctx)
    else:
        raise Http404


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
@mobile_only
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
def save_decklist(request, decklist_id=None):
    data = json.loads(request.body.decode('UTF-8'))
    decklist_data = data['decklist_data']
    if 'is_public' in data:
        is_public = data['is_public']
    else:
        is_public = True

    # Check user matches the decklist
    decklist = get_object_or_404(DeckList, pk=decklist_id, profile__user=request.user)
    decklist.name = decklist_data['name']
    decklist.comments = decklist_data['comments']
    decklist.public = is_public
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
            try:
                DeckListCard.objects.get_or_create(
                    decklist=decklist,
                    card=card,
                    position=card_data['position'],
                    zone=user_zone,
                    quantity=card_data['quantity']
                )
            except ValueError:  # Probably user input error somehow, like putting 'e' in the quantity
                pass
        zone_count += 1

    return JsonResponse({'decklist_pk': decklist.pk})


def private_decklist(request):
    return render(request, 'cardDatabase/html/private_decklist.html')


def view_decklist(request, decklist_id):
    decklist = get_object_or_404(DeckList, pk=decklist_id)
    if not decklist.public and not request.user == decklist.profile.user and not request.user.is_superuser:
        return HttpResponseRedirect(reverse('cardDatabase-private-decklist'))

    cards = decklist.cards.all()
    zones = UserDeckListZone.objects.filter(decklist=decklist).order_by('position').values_list('zone__name', flat=True).distinct()

    '''
    DeckListCard is not the same as Card so compare the pk's by using values_list to get Card objects from DeckListCard
    Also avoids duplicate named/reprinted cards needing multiple banlist entries
    '''
    deck_card_names = list(cards.values_list('card__name', flat=True))
    banned_cards = BannedCard.objects.all()
    ban_warnings = []
    for banned_card in banned_cards:
        if banned_card.card.name in deck_card_names:
            ban_warnings.append({
                'format': banned_card.format.name,
                'card': banned_card.card.name,
                'card_img_url': banned_card.card.card_image.url,
                'view_card_url': reverse('cardDatabase-view-card', kwargs={'card_id': banned_card.card.card_id})
            })

    combination_bans = CombinationBannedCards.objects.all()
    combination_ban_warnings = []
    for combination_ban in combination_bans:
        combination_banned_cards = combination_ban.cards.all()
        combination_banned_card_names = combination_banned_cards.values_list('name', flat=True)
        overlap = set(combination_banned_card_names) & set(deck_card_names)
        if len(overlap) > 1:
            combination_ban_warning = {
                'format': combination_ban.format.name,
                'cards': [],
            }
            for card in combination_banned_cards:
                if card.name in overlap:
                    combination_ban_warning['cards'].append({
                        'name': card.name,
                        'image_url': card.card_image.url,
                        'view_card_url': reverse('cardDatabase-view-card',
                                                 kwargs={'card_id': card.card_id})
                    })
            combination_ban_warnings.append(combination_ban_warning)

    return render(request, 'cardDatabase/html/view_decklist.html', context={
        'decklist': decklist,
        'zones': zones,
        'cards': cards,
        'ban_warnings': ban_warnings,
        'combination_ban_warnings': combination_ban_warnings,
    })


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


def mobile_only(request):
    return render(request, 'cardDatabase/html/mobile_only.html', {})


@login_required
def copy_decklist(request, decklist_id=None):
    try:
        original_decklist = DeckList.objects.get(pk=decklist_id)
    except DeckList.DoesNotExist:
        return HttpResponseRedirect(reverse('cardDatabase-user-decklists'))

    new_decklist = DeckList.objects.create(profile=request.user.profile, name=original_decklist.name,
                                           comments=original_decklist.comments)
    cards = DeckListCard.objects.filter(decklist__pk=original_decklist.pk)
    original_zones = UserDeckListZone.objects.filter(decklist__pk=original_decklist.pk)

    for zone in original_zones:
        UserDeckListZone.objects.create(decklist=new_decklist, position=zone.position, zone=zone.zone)

    for card in cards:
        zone = UserDeckListZone.objects.get(decklist=new_decklist, position=card.zone.position, zone=card.zone.zone)
        DeckListCard.objects.create(decklist=new_decklist, card=card.card, position=card.position, zone=zone, quantity=card.quantity)

    if request.user_agent.is_mobile or request.user_agent.is_tablet:
        return HttpResponseRedirect(reverse('cardDatabase-edit-decklist-mobile', kwargs={'decklist_id': new_decklist.pk}))
    else:
        return HttpResponseRedirect(reverse('cardDatabase-edit-decklist', kwargs={'decklist_id': new_decklist.pk}))


@csrf_exempt
@require_POST
@reddit_bot
def reddit_bot_query(request):
    try:
        data = json.loads(request.body.decode('UTF-8'))
    except (json.JSONDecodeError, json.decoder.JSONDecodeError):
        return HttpResponse('Error loading json', status=401)
    words = data.get('keywords', None)
    if not words:
        return HttpResponse('No keywords provided', status=400)
    flags = data.get('flags', [])

    exact_query = False
    if 'e' in flags:
        exact_query = True

    all_sides = False
    if 'b' in flags:
        all_sides = True

    reverse_sort = False
    if 'a' in flags:
        reverse_sort = True

    adv_form = AdvancedSearchForm(request.POST)
    if not adv_form.is_valid():  # Have to run is_valid to access cleaned_data
        return HttpResponse('Unknown error occured', status=500)
    adv_form.cleaned_data['generic_text'] = ' '.join(words)
    adv_form.cleaned_data['text_exactness'] = CONS.TEXT_EXACT if exact_query else CONS.TEXT_CONTAINS_ALL
    adv_form.cleaned_data['sort_by'] = CONS.DATABASE_SORT_BY_MOST_RECENT
    adv_form.cleaned_data['reverse_sort'] = reverse_sort
    adv_form.cleaned_data['text_search_fields'] = ['name']
    cards = advanced_search(adv_form)
    ctx = {'cards': []}
    card = None
    if len(cards['cards']):
        card = cards['cards'][0]
    if card:
        ctx['cards'].append({
            'name': card.name,
            'image_url': request.build_absolute_uri(card.card_image.url),
            'view_card_url': request.build_absolute_uri(reverse('cardDatabase-view-card', kwargs={'card_id': card.card_id}))
        })
        if all_sides:
            for other_side in card.other_sides:
                ctx['cards'].append({
                    'name': other_side.name,
                    'image_url': request.build_absolute_uri(other_side.card_image.url),
                    'view_card_url': request.build_absolute_uri(reverse('cardDatabase-view-card', kwargs={'card_id': other_side.card_id}))
                })

    return JsonResponse(ctx)


def metrics(request):
    ctx = {
        'most_picked_cards': MostPickedCardPickRate.objects.all().order_by('-percentage'),
        'attribute_picks': AttributePickRate.objects.all().order_by('-percentage'),
        'total_cost_picks': CardTotalCostPickRate.objects.all().order_by('-total_cost'),
        'card_type_picks': CardTypePickRate.objects.all().order_by('-percentage'),
        'pick_periods': PickPeriod.objects.all()
    }
    return render(request, 'cardDatabase/html/metrics.html', ctx)