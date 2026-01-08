from django.core.management.base import BaseCommand

from cardDatabase.models.Banlist import Format, BannedCard, CombinationBannedCards
from cardDatabase.models.CardType import Card
from fowsim import constants as CONS


class Command(BaseCommand):
    help = "Creates all Format, BannedCard and CombinationBannedCard objects in the database if they dont already exist"

    def handle(self, *args, **options):
        for format_data in CONS.BANNED_CARDS:
            format_name = format_data["format_name"]
        f, created = Format.objects.get_or_create(name=format_name)
        for banned_card_id in format_data["cards"]:
            BannedCard.objects.get_or_create(format=f, card=Card.objects.get(card_id=banned_card_id))

        # Effort to work out if they exist or not, just nuke and rebuild, there isnt many
        CombinationBannedCards.objects.all().delete()
        for combination_banned_cards in format_data["combination_bans"]:
            combination_ban = CombinationBannedCards.objects.create(format=f)
            for card_id in combination_banned_cards:
                combination_ban.cards.add(Card.objects.get(card_id=card_id))
