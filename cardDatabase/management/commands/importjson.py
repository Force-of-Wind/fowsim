import json
import re

from django.core.management.base import BaseCommand
from django.core.management import call_command

from fowsim import constants as CONS
from cardDatabase.models.CardType import Card, AbilityText, Race, Type


#  Types separated by / that don't have spaces e.g. "Chant / Rune".
#  Need to distinguish between Addition:J/Resonator for ex
MIXED_TYPES = ['Chant/Rune/Master Rune', 'Chant/Rune', 'Special Magic Stone/True Magic Stone']


def strip_attributes(text):
    # Magic stone have types 'Fire Magic Stone', etc. Remove that, then strip whitespace
    for attribute in CONS.ATTRIBUTE_NAMES:
        text = text.replace(attribute, '')
    return text.strip()


PUNCTUATION_REPLACEMENTS = {
    'ӧ': 'o',
    'ö': 'o',  # There are actually two different ones, not a mistake. One is cyrillic, one is latin.
}


def remove_punctuation(name):
    matches = re.findall('[^a-zA-Z0-9 ]', name)
    for match in matches:
        if match in PUNCTUATION_REPLACEMENTS:
            name = name.replace(match, PUNCTUATION_REPLACEMENTS[match])
        else:
            name = name.replace(match, '')
    return name


NAME_ERRORS = {
    'ӧ': 'ö'  # Not the same
}


def replace_name_errors(name):
    for error in NAME_ERRORS:
        name = name.replace(error, NAME_ERRORS[error])
    return name


class Command(BaseCommand):
    help = 'imports cardDatabase/static/cards.json to the database'

    def handle(self, *args, **options):
        with open('cardDatabase/static/cards.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
            for cluster in data['fow']['clusters']:
                sets = cluster['sets']
                for fow_set in sets:
                    cards = fow_set['cards']
                    for card in cards:
                        for unused_set in CONS.UNSEARCHED_DATABASE_SETS:  # Mostly just old Valhalla
                            if card['id'].startswith(unused_set):
                                break
                        else:
                            # In a used set
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
                                name=replace_name_errors(card['name']),
                                name_without_punctuation=remove_punctuation(card['name']),
                                card_id=card['id'].replace('*', CONS.DOUBLE_SIDED_CARD_CHARACTER),
                                cost=card['cost'] or None,
                                divinity=card['divinity'].replace("∞", CONS.INFINITY_STRING) or None,
                                flavour=card['flavor'] or None,
                                rarity=card['rarity'],
                                ATK=card['ATK'] or None,
                                DEF=card['DEF'] or None,
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
        call_command('assign_existing_card_images')
