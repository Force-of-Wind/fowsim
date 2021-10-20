import json

from fowsim import constants as CONS
from django.core.management.base import BaseCommand
from cardDatabase.models.CardType import Card, AbilityText, Race, Type


#  Types separated by / that don't have spaces e.g. "Chant / Rune".
#  Need to distinguish between Addition:J/Resonator for ex
MIXED_TYPES = ['Chant/Rune/Master Rune', 'Chant/Rune', 'Special Magic Stone/True Magic Stone']


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
                sets = cluster['sets']
                for fow_set in sets:
                    cards = fow_set['cards']
                    for card in cards:
                        card_types = []

                        for card_type in card['type'].split(' / '):
                            if any(x in card_type for x in MIXED_TYPES):
                                for mixed_type in MIXED_TYPES:
                                    if mixed_type in card_type:
                                        card_types = card_types + mixed_type.split('/')
                            else:
                                card_types.append(card_type)

                        card_races = card['race']
                        card_abilities = card['abilities']
                        card, created = Card.objects.get_or_create(
                            name=card['name'],
                            card_id=card['id'].replace('*', CONS.DOUBLE_SIDED_CARD_CHARACTER),
                            cost=card['cost'],
                            divinity=card['divinity'],
                            flavour=card['flavor'],
                            rarity=card['rarity'],
                            ATK=card['ATK'],
                            DEF=card['DEF'],
                        )
                        for card_ability in card_abilities:
                            ability_text, created = AbilityText.objects.get_or_create(text=card_ability)
                            card.ability_texts.add(ability_text)
                        for card_race in card_races:
                            race, created = Race.objects.get_or_create(name=card_race)
                            card.races.add(race)
                        for card_type in card_types:
                            type_obj, created = Type.objects.get_or_create(name=card_type)
                            card.types.add(type_obj)

                        card.save()
