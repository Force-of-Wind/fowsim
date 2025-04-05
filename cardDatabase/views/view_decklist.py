from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from cardDatabase.models import DeckList, BannedCard, CombinationBannedCards
from cardDatabase.models.DeckList import UserDeckListZone
from cardDatabase.models.Rulings import Restriction, RestrictionException
from django.db.models import Q

from fowsim import constants as CONS


def get(request, decklist_id, share_parameter=''):
    decklist = get_object_or_404(DeckList, pk=decklist_id)
    if (not decklist.public and not request.user == decklist.profile.user and not request.user.is_superuser) and (
            share_parameter == '' or not decklist.shareCode == share_parameter):
        return HttpResponseRedirect(reverse('cardDatabase-private-decklist'))

    cards = decklist.cards.all()
    zones = UserDeckListZone.objects.filter(decklist=decklist).order_by('position').values_list('zone__name',
                                                                                                flat=True).distinct()

    ''' 
    DeckListCard is not the same as Card so compare the pk's by using values_list to get Card objects from DeckListCard
    Also avoids duplicate named/reprinted cards needing multiple banlist entries
    '''
    deck_card_names = list(cards.values_list('card__name', flat=True))

    if decklist.deck_format != CONS.PARADOX_FORMAT:
        banned_cards = BannedCard.objects.filter(format=decklist.deck_format)
        combination_bans = CombinationBannedCards.objects.filter(format=decklist.deck_format)
    else:
        query = Q(format=decklist.deck_format)
        query |= Q(format=CONS.WANDERER_FORMAT)
        banned_cards = BannedCard.objects.filter(query)
        combination_bans = CombinationBannedCards.objects.filter(query)

    ban_warnings = []
    for banned_card in banned_cards:
        if banned_card.card.name in deck_card_names:
            ban_warnings.append({
                'format': banned_card.format.name,
                'card': banned_card.card.name,
                'card_img_url': banned_card.card.card_image.url,
                'view_card_url': reverse('cardDatabase-view-card', kwargs={'card_id': banned_card.card.card_id})
            })

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

    restrictions = Restriction.objects.all()
    deck_restrictions = []
    for restriction in restrictions:
        exceptions = RestrictionException.objects.filter(restriction=restriction)
        deck_exceptions = []
        for exception in exceptions:
            cards_exception_applies_to = []
            for card in exception.exception_action.applying_to_cards.all():
                cards_exception_applies_to.append(card.id)
            deck_exceptions.append({
                'exceptionApplyingCard': exception.exception_applying_card.id,
                'exceptionApplyingZone': exception.card_zone_restriction,
                'exceptionAction': exception.exception_action.technical_name,
                'cardExceptionAppliesTo': cards_exception_applies_to
            })

        deck_restrictions.append({
            'text': restriction.text,
            'action': restriction.action.technical_name,
            'checkingTag': restriction.tag.id,
            'restrictedTag': restriction.restricted_tag.id,
            'exceptions': deck_exceptions
        })

    cardsData = []
    for card in cards:
        tags = []
        for tag in card.card.tag.all():
            tags.append(tag.id)
        cardsData.append({
            'quantity': card.quantity,
            'tags': tags,
            'id': card.card.id,
            'zone': card.zone.zone.name
        })

    return render(request, 'cardDatabase/html/view_decklist.html', context={
        'decklist': decklist,
        'zones': zones,
        'cards': cards,
        'ban_warnings': ban_warnings,
        'combination_ban_warnings': combination_ban_warnings,
        'deckRestrictions': deck_restrictions,
        'cardsData': cardsData
    })
