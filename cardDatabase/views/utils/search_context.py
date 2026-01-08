from django.forms import MultipleChoiceField

from cardDatabase.models import PickPeriod, DeckList, Format
from cardDatabase.models.CardType import Race, Card, CardArtist
from fowsim import constants as CONS
from django.db.models import Q, Count, F

import re


def apply_text_search(cards, text, search_fields, exactness_option):
    if not text:
        return cards

    words = [w for w in text.split(" ") if w]
    if not words:
        return cards

    if "name" in search_fields:
        search_fields = search_fields + ["name_without_punctuation"]

    if exactness_option == CONS.TEXT_CONTAINS_AT_LEAST_ONE:
        q = Q()
        for word in words:
            word_query = Q()
            for search_field in search_fields:
                word_query |= Q(**{search_field + "__icontains": word})
            q |= word_query
        output = cards.filter(q)

    elif exactness_option == CONS.TEXT_CONTAINS_ALL:
        # Build a single combined Q object instead of chaining .filter() calls
        # Chaining filters on related fields creates multiple JOINs which is slow
        combined_q = Q()
        for word in words:
            word_query = Q()
            for search_field in search_fields:
                word_query |= Q(**{search_field + "__icontains": word})
            combined_q &= word_query
        output = cards.filter(combined_q)

    elif exactness_option == CONS.TEXT_EXACT:
        q = Q()
        for search_field in search_fields:
            q |= Q(**{search_field + "__icontains": text})
        output = cards.filter(q)

    else:
        return cards

    return output


def basic_search(basic_form):
    cards = []
    if basic_form.is_valid():
        search_text = basic_form.cleaned_data["generic_text"]
        set_query = Q()
        format_string = basic_form.cleaned_data["format"]
        if format_string:
            format = Format.objects.get(name=format_string)
            if format.sets.count() > 0:
                set_query = get_set_query(list(format.sets.values_list("code", flat=True).distinct()), True)

        cards = Card.objects.filter(set_query).exclude(get_unsupported_sets_query()).distinct()
        cards = apply_text_search(cards, search_text, ["name", "ability_texts__text"], CONS.TEXT_CONTAINS_ALL)
    cards = sort_cards(cards, CONS.DATABASE_SORT_BY_MOST_RECENT, False)
    return {"cards": cards}


def advanced_search(advanced_form):
    ctx = {}
    cards = []
    if advanced_form.is_valid():
        ctx["advanced_form_data"] = advanced_form.cleaned_data

        attr_query, attr_annotation, attr_extra_queries, attr_exclusions = get_attr_query(
            advanced_form.cleaned_data["colours"],
            advanced_form.cleaned_data["colour_match"],
            advanced_form.cleaned_data["colour_combination"],
        )
        race_query = get_race_query(advanced_form.cleaned_data["race"])
        artist_query = get_artist_query(advanced_form.cleaned_data["artist"])
        set_query = get_set_query(advanced_form.cleaned_data["sets"])

        format_string = advanced_form.cleaned_data["format"]
        if format_string:
            format = Format.objects.get(name=format_string)
            if format.sets.count() > 0:
                set_query = get_set_query(list(format.sets.values_list("code", flat=True).distinct()), True)
                ctx["advanced_form_data"]["sets"] = []

        card_type_query = get_card_type_query(advanced_form.cleaned_data["card_type"])
        rarity_query = get_rarity_query(advanced_form.cleaned_data["rarity"])
        divinity_query = get_divinity_query(advanced_form.cleaned_data["divinity"])
        atk_query = get_atk_def_query(
            advanced_form.cleaned_data["atk_value"], advanced_form.cleaned_data["atk_comparator"], "ATK"
        )
        def_query = get_atk_def_query(
            advanced_form.cleaned_data["def_value"], advanced_form.cleaned_data["def_comparator"], "DEF"
        )
        keywords_query = get_keywords_query(advanced_form.cleaned_data["keywords"])
        solo_mode_query = get_solo_mode_query(advanced_form.cleaned_data["solo_mode"])

        cards = (
            Card.objects.annotate(**attr_annotation)
            .filter(attr_query)
            .exclude(attr_exclusions)
            .filter(race_query)
            .filter(artist_query)
            .filter(set_query)
            .filter(card_type_query)
            .filter(rarity_query)
            .filter(divinity_query)
            .filter(atk_query)
            .filter(def_query)
            .filter(keywords_query)
            .filter(solo_mode_query)
            .exclude(get_unsupported_sets_query())
            .distinct()
        )

        for q in attr_extra_queries:
            cards = cards.filter(q)

        cards = apply_text_search(
            cards,
            advanced_form.cleaned_data["generic_text"],
            advanced_form.cleaned_data["text_search_fields"],
            advanced_form.cleaned_data["text_exactness"],
        )

        cost_filters = advanced_form.cleaned_data["cost"]
        if len(cost_filters) > 0:
            # Don't need DB query to do total cost, remove all that don't match if any were chosen
            if "X" in cost_filters:
                cards = [x for x in cards if str(x.total_cost) in cost_filters or x.cost and "{X}" in x.cost]
            else:
                cards = [x for x in cards if str(x.total_cost) in cost_filters]

        cards = sort_cards(
            cards,
            advanced_form.cleaned_data["sort_by"],
            advanced_form.cleaned_data["reverse_sort"] or False,
            advanced_form.cleaned_data["pick_period"] or None,
        )
    return ctx | {"cards": cards}


def get_search_form_ctx():
    try:
        race_values = Race.objects.values("name")
        races_list = list(map(lambda x: x["name"], race_values))  # Remove blank string
        races_list.sort()
        races_list.remove("")

        artist_values = CardArtist.objects.values("name")
        artists_list = list(map(lambda x: x["name"], artist_values))
        artists_list.sort()
        if "" in artists_list:
            artists_list.remove("")  # Remove blank string if exists

        format_list = Format.objects.annotate(num_sets=Count("sets")).filter(num_sets__gt=0).values("name")
    except Exception:
        races_list = []
        artists_list = []
        format_list = []

    return {
        "races_list": list(races_list),
        "artists_list": list(artists_list),
        "format_list": list(format_list),
        "card_types_list": CONS.DATABASE_CARD_TYPE_GROUPS,
        "sets_json": CONS.SET_DATA,
    }


def get_race_query(data):
    race_query = Q()
    for race in data:
        race_query |= Q(races__name=race)
    return race_query


def get_artist_query(data):
    artist_query = Q()
    for artist in data:
        artist_query |= Q(artists__name=artist)
    return artist_query


def get_not_card_race_query(data):
    card_race_query = ~Q()
    for card_race in data:
        card_race_query &= ~Q(races__name=card_race)
    return card_race_query


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


def get_not_card_type_query(data):
    card_type_query = ~Q()
    for card_type in data:
        card_type_query &= ~Q(types__name=card_type)
    return card_type_query


def get_card_prefix_query(data):
    card_prefix_query = Q()
    for prefix in data:
        card_prefix_query |= Q(card_id__startswith=prefix)
    return card_prefix_query


def get_not_card_prefix_query(data):
    card_prefix_query = ~Q()
    for prefix in data:
        card_prefix_query &= ~Q(card_id__startswith=prefix)
    return card_prefix_query


def get_set_query(data, strict_search=False):
    set_query = Q()
    for fow_set in data:
        if fow_set in CONS.SEARCH_SETS_INCLUDE and not strict_search:
            #  Search implies more than just itself, e.g. AO3 includes AO3 Buy a Box, so that those sets too
            for also_included_set in CONS.SEARCH_SETS_INCLUDE[fow_set]:
                # No trailing '-' because the '-' is included in CONS
                set_query |= Q(card_id__istartswith=also_included_set)
        set_query |= Q(card_id__istartswith=fow_set + "-")

        # Search for sets directly when in strict_search mode (promos like BAB wont show otherwise)
        if strict_search:
            set_query |= Q(card_id=fow_set)
    return set_query


def get_simple_set_query(data):
    set_query = Q()
    for fow_set in data:
        set_query |= Q(card_id__istartswith=fow_set + "-")
    return set_query


def get_not_set_query(data):
    set_query = ~Q()
    for fow_set in data:
        set_query &= ~Q(card_id__istartswith=fow_set + "-")
    return set_query


def get_attr_query(data, colour_match, colour_combination):
    extra_queries = []
    attr_query = Q()
    attr_exclusions = Q()
    attr_annotation = {"colour_combination_count": Count("colours__db_representation", distinct=True)}
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
        #  It's inefficient so try to avoid using it if possible since it does another db call for each query
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
        return Q(**{f"{field_name}__{comparator}": value})
    return Q()


def get_keywords_query(data):
    keywords_query = Q()
    for search_string in data:
        for keyword in search_string.split(","):
            keywords_query |= Q(ability_texts__text__icontains=keyword)
    return keywords_query


def get_solo_mode_query(solo_mode):
    solo_mode_query = Q()
    if solo_mode:
        solo_mode_query = Q(ability_styles__identifier=CONS.SOLO_MODE_STYLE)
    return solo_mode_query


def get_set_number_sort_value(set_number):
    #  Need to sort them backwards since it gets reversed to show most recent first
    #  Just make them a negative integer of itself (removing characters)
    if set_number:
        num = re.sub("[^0-9]", "", set_number)  # Remove non-numeric
        if num.isnumeric():
            return -1 * int(num)
    return float("-inf")


def get_deck_format_query(data):
    deck_format_query = Q()
    for deck_format in data:
        deck_format_query |= Q(deck_format__name=deck_format)
    return deck_format_query


def sort_cards(cards, sort_by, is_reversed, pick_time_period=None):
    if sort_by == CONS.DATABASE_SORT_BY_MOST_RECENT or not sort_by:
        return sorted(
            cards,
            key=lambda item: (
                CONS.SETS_IN_ORDER.index(item.set_code) if item.set_code in CONS.SETS_IN_ORDER else 999999,
                get_set_number_sort_value(item.set_number),
            ),
            reverse=not is_reversed,
        )  # (last set comes first, flip the reversed flag
    elif sort_by == CONS.DATABASE_SORT_BY_TOTAL_COST:
        return sorted(
            cards,
            key=lambda item: (
                item.total_cost,
                -CONS.SETS_IN_ORDER.index(item.set_code) if item.set_code in CONS.SETS_IN_ORDER else 999999,
                get_set_number_sort_value(item.set_number),
            ),
            reverse=is_reversed,
        )
    elif sort_by == CONS.DATABASE_SORT_BY_ALPHABETICAL:
        return sorted(
            cards,
            key=lambda item: (
                item.name,
                CONS.SETS_IN_ORDER.index(item.set_code) if item.set_code in CONS.SETS_IN_ORDER else 999999,
                get_set_number_sort_value(item.set_number),
            ),
            reverse=is_reversed,
        )
    elif sort_by == CONS.DATABASE_SORT_BY_POPULARITY:
        if pick_time_period is None:
            pick_time_period = CONS.PICK_PERIOD_NINETY_DAYS
        all_time = pick_time_period == str(CONS.PICK_PERIOD_ALL_TIME)
        pick_period = PickPeriod.objects.get(days=pick_time_period, all_time=all_time)
        return (
            cards.prefetch_related("popularities")
            .filter(Q(popularities__isnull=True) | Q(popularities__period=pick_period))
            .order_by(F("popularities__percentage").desc(nulls_last=True))
        )
    raise Exception("Attempting to sort card by invalid selection")


def get_unsupported_sets_query():
    unsupported_sets = Q()
    for unsupported_set in CONS.UNSEARCHED_DATABASE_SETS:
        unsupported_sets |= Q(card_id__istartswith=unsupported_set)

    return unsupported_sets


def get_unsupported_decklists_query():
    unsuported_decklists = Q()
    unsuported_decklists |= Q(public=False)
    unsuported_decklists |= Q(cards__quantity__isnull=True)

    return unsuported_decklists


def get_form_from_params(form_class, request):
    # Grab what query params from request.GET match the expected form values and put them into the dictionary input_data
    # Then instantiate the form using those values
    input_data = {}
    for form_field_name in form_class.__dict__["declared_fields"]:
        if type(form_class.__dict__["declared_fields"][form_field_name]) == MultipleChoiceField:
            query_param_value = request.GET.getlist(form_field_name, None)
        else:
            query_param_value = request.GET.get(form_field_name, None)
        if query_param_value:
            input_data[form_field_name] = query_param_value
    return form_class(input_data)


def decklist_search(decklist_form):
    decklists = []
    if decklist_form.is_valid():
        search_text = decklist_form.cleaned_data["contains_card"]
        text_exactness = decklist_form.cleaned_data["text_exactness"]
        deck_format_filter = get_deck_format_query(decklist_form.cleaned_data["deck_format"])
        decklists = DeckList.objects.exclude(get_unsupported_decklists_query()).distinct()
        decklists = decklists.filter(deck_format_filter)
        decklists = apply_deckcard_cardname_search(decklists, search_text, ["name"], text_exactness)
        decklists = decklists.order_by("-last_modified")

    return decklists


def apply_deckcard_cardname_search(decklists, text, search_fields, exactness_option):
    if not text:
        return decklists

    exactness_option = exactness_option or CONS.TEXT_CONTAINS_ALL

    output = []
    words = text.split(" ")
    if "name" in search_fields:
        search_fields.append("name_without_punctuation")

    if exactness_option == CONS.TEXT_CONTAINS_AT_LEAST_ONE:
        q = Q()
        for word in words:
            word_query = Q()
            for search_field in search_fields:
                word_query |= Q(**{"cards__card__" + search_field + "__icontains": word})
            q |= word_query
        output = decklists.filter(q)

    elif exactness_option == CONS.TEXT_CONTAINS_ALL:
        # Use db because there's not many terms and this is more efficient
        output = decklists
        for word in words:
            word_query = Q()
            for search_field in search_fields:
                word_query |= Q(**{"cards__card__" + search_field + "__icontains": word})

            output = output.filter(word_query)

    elif exactness_option == CONS.TEXT_EXACT:
        q = Q()
        for search_field in search_fields:
            q |= Q(**{"cards__card__" + search_field + "__icontains": text})

        output = decklists.filter(q)

    return output


def full_set_code_to_name(set_code):
    for cluster in CONS.SET_DATA["clusters"]:
        for fow_set in cluster["sets"]:
            if fow_set["code"] == set_code:
                return fow_set["name"]


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
