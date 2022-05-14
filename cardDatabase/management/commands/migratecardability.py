from django.core.management.base import BaseCommand

from cardDatabase.models.CardType import Card, CardAbility


class Command(BaseCommand):
    help = 'Migrates data from ability_texts to ability_text using through model'

    def handle(self, *args, **options):
        for card in Card.objects.all():
            position = 1
            for text in card.ability_texts.all():
                CardAbility.objects.get_or_create(card=card, ability_text=text, position=position)
                position += 1
