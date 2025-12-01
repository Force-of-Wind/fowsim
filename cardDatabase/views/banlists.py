from cardDatabase.models import BannedCard, CombinationBannedCards

from django.views.decorators.cache import cache_page
from django.shortcuts import render

@cache_page(60 * 60)  # 1h
def get(request):
    ctx = {}
    banned_cards_by_format = {}
    combination_banned_cards_by_format = {}

    #  Used to avoid duplicates (by name(s))
    seen_banned_cards_by_format = {}
    seen_combination_banned_cards_by_format = {}

    for banned_card in BannedCard.objects.select_related("card", "format"):
        format_name = banned_card.format.name
        card_name = banned_card.card.name
        if format_name not in banned_cards_by_format:
            banned_cards_by_format[format_name] = []
            seen_banned_cards_by_format[format_name] = set()
        
        if card_name not in seen_banned_cards_by_format[format_name]:
            banned_cards_by_format[format_name].append(banned_card)
            seen_banned_cards_by_format[format_name].add(card_name)



    for combination_banned_card in CombinationBannedCards.objects.select_related("format").prefetch_related("cards"):
        if combination_banned_card.format.name not in combination_banned_cards_by_format:
            combination_banned_cards_by_format[combination_banned_card.format.name] = []
            seen_combination_banned_cards_by_format[combination_banned_card.format.name] = set()

    ctx['banned_cards'] = banned_cards_by_format
    ctx['combination_banned_cards'] = combination_banned_cards_by_format

    return render(request, 'cardDatabase/html/banlists.html', ctx)

    