import json

from fowsim import constants as CONS
from django.core.management.base import BaseCommand
from cardDatabase.models.CardType import Card, AbilityText, Race


def strip_attributes(text):
    # Magic stone have types 'Fire Magic Stone', etc. Remove that, then strip whitespace
    for attribute in CONS.ATTRIBUTE_NAMES:
        text = text.replace(attribute, '')
    return text.strip()


class Command(BaseCommand):
    help = 'imports cardDatabase/static/cards.json to the database'

    def handle(self, *args, **options):
        with open('cardDatabase/static/cards.json') as json_file:
            data = json.load(json_file)
            for cluster in data['fow']['clusters']:
                cluster_name = cluster['name']
                sets = cluster['sets']
                for fow_set in sets:
                    set_name = fow_set['name']
                    set_code = fow_set['code']
                    cards = fow_set['cards']
                    for card in cards:
                        card_types = card['type']
                        card_types = [strip_attributes(x) for x in card_types.split('/')]
                        card_rarity = card['rarity']

                        # Some rulers are Uncommon/Rare, set them to modern Ruler value
                        if (CONS.RARITY_RULER in card_types and not card_rarity == CONS.RARITY_ASCENDED_RULER_VALUE and
                                not card_rarity == CONS.RARITY_ASCENDED_J_RULER_VALUE):
                            card_rarity = CONS.RARITY_RULER_VALUE

                        card_races = card['race']
                        card_abilities = card['abilities']
                        card, created = Card.objects.get_or_create(
                            name=card['name'],
                            card_id=card['id'],
                            cost=card['cost'],
                            divinity=card['divinity'],
                            flavour=card['flavor'],
                            rarity=card_rarity,
                            ATK=card['ATK'],
                            DEF=card['DEF'],
                        )
                        for card_ability in card_abilities:
                            ability_text, created = AbilityText.objects.get_or_create(text=card_ability)
                            card.ability_texts.add(ability_text)
                        for card_race in card_races:
                            race, created = Race.objects.get_or_create(name=card_race)
                            card.races.add(race)

                        card.save()
