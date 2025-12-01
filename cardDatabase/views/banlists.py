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
    #  Sort the tuples of combinations alphabetically so we can find them later as equals
    seen_combination_banned_cards_by_format = {}

    for banned_card in BannedCard.objects.select_related("card", "format"):
        format_name = banned_card.format.name
        card_name = banned_card.card.name

        #  Setup data structures if they don't exist
        if format_name not in banned_cards_by_format:
            banned_cards_by_format[format_name] = []
            seen_banned_cards_by_format[format_name] = set()

        #  Add card
        if card_name not in seen_banned_cards_by_format[format_name]:
            banned_cards_by_format[format_name].append(banned_card)
            seen_banned_cards_by_format[format_name].add(card_name)

    for combination_banned_card in CombinationBannedCards.objects.select_related(
        "format"
    ).prefetch_related("cards"):
        format_name = combination_banned_card.format.name
        
        #  Setup data structuyres if they don't exist
        if format_name not in combination_banned_cards_by_format:
            combination_banned_cards_by_format[combination_banned_card.format.name] = []
            seen_combination_banned_cards_by_format[
                combination_banned_card.format.name
            ] = set()

        #  Add combinations
        card_names = tuple(sorted(combination_banned_card.cards.values_list('name', flat=True)))
        if card_names not in seen_combination_banned_cards_by_format[format_name]:
            combination_banned_cards_by_format[format_name].append(combination_banned_card)
        

    ctx["banned_cards"] = banned_cards_by_format
    ctx["combination_banned_cards"] = combination_banned_cards_by_format
    ctx["seen_formats"] = seen_combination_banned_cards_by_format.keys() | seen_banned_cards_by_format.keys()

    print(ctx["combination_banned_cards"])

    return render(request, "cardDatabase/html/banlists.html", ctx)
