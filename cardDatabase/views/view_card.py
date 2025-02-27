from django.shortcuts import get_object_or_404, render

from cardDatabase.forms import SearchForm, AdvancedSearchForm
from cardDatabase.models import Card, DeckList
from cardDatabase.views.utils.search_context import get_search_form_ctx, searchable_set_and_name, sort_cards, \
    get_set_query
from fowsim import constants as CONS

import datetime


def get(request, card_id=None):
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
                                                      last_modified__gt=one_month_ago).distinct().order_by(
        '-last_modified')
    if not ctx['recent_decklists'].count():
        # There are no recent ones, just grab the up to the 4 most recent ones instead
        ctx['recent_decklists'] = DeckList.objects.filter(public=True, cards__card__in=(
                    [card] + list(card.other_sides))).distinct().order_by('-last_modified')[:4]

    return render(request, 'cardDatabase/html/view_card.html', context=ctx)


def get_next_prev_cards(card_id, set_code):
    # get card number from card_id
    try:
        card_id_int = card_id.split("-")[-1]
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
    except ValueError:  # Other unusual set codes like NWE-SEC4
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
        current_set_index = next((index for index, elem in enumerate(CONS.SET_CHOICES) if elem[0] == set_code), 0)

        if current_set_index == 0 and offset > 0:  # This is the last set, don't show a next
            return None

        try:
            new_set_code = CONS.SET_CHOICES[current_set_index - offset][0]
        except IndexError:  # No sets before or after, depending on offset
            new_set_code = None

        # check that new_set_code has been set, otherwise immediately return '', if new_set_code not set, it means we
        # have reached the beginning or end of all cards in our card database
        if new_set_code:
            # if we are setting the previous card (i.e. previous set), offset will be -1
            if offset < 0:
                # put new_set_code (string) into an array
                set_code_arr = new_set_code.split()

                # get all cards in the new set, the [0]th element card will be the LAST card in this set
                all_cards_in_new_set = sort_cards(Card.objects.filter(get_set_query(set_code_arr)), False, True)

                # set new card id to the last card's card id, in the PREVIOUS set
                new_card_id = None
                if all_cards_in_new_set:
                    new_card_id = all_cards_in_new_set[0].card_id
            else:
                # set new card id to the NEXT set (where we start from the 1st card, XXX-001
                new_card_id = new_set_code + "-001"

            if new_card_id and Card.objects.filter(card_id=new_card_id).exists():
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
