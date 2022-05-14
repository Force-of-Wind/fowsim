import json
import re

from django.core.management.base import BaseCommand
from django.core.management import call_command

from fowsim import constants as CONS
from cardDatabase.models.CardType import Card, AbilityText, Race, Type, CardColour, CardAbility
from cardDatabase.models.DeckList import DeckListZone


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


def get_colour_name(code):
    for choice_code, choice_name in CONS.COLOUR_CHOICES:
        if code == choice_code:
            return choice_name



def setup_db():
    for zone in CONS.ZONES_SHOWN_BY_DEFAULT:
        DeckListZone.objects.get_or_create(name=zone, show_by_default=True)


class Command(BaseCommand):
    help = 'imports cardDatabase/static/cards.json to the database'

    def handle(self, *args, **options):
        with open('cardDatabase/static/cards.json', encoding='utf-8') as json_file:
            setup_db()
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
                            card_colours = card['colour']
                            card, created = Card.objects.get_or_create(
                                name=replace_name_errors(card['name']),
                                name_without_punctuation=remove_punctuation(card['name']),
                                card_id=card['id'].replace('*', CONS.DOUBLE_SIDED_CARD_CHARACTER),
                                cost=card['cost'] or None,
                                divinity=card['divinity'].replace("∞", CONS.INFINITY_STRING) or None,
                                flavour=card['flavour'] or None,
                                rarity=card['rarity'],
                                ATK=card['ATK'] or None,
                                DEF=card['DEF'] or None,
                            )
                            position = 1
                            for card_ability in card_abilities:
                                ability_text, created = AbilityText.objects.get_or_create(text=card_ability.strip())
                                CardAbility.objects.get_or_create(ability_text=ability_text, card=card, position=position)
                                position += 1
                            for card_race in card_races:
                                race, created = Race.objects.get_or_create(name=card_race.strip())
                                card.races.add(race)
                            for card_type in card_types:
                                type_obj, created = Type.objects.get_or_create(name=card_type.strip())
                                card.types.add(type_obj)
                            for card_colour in card_colours:
                                colour_obj, created = CardColour.objects.get_or_create(db_representation=card_colour.strip(), name=get_colour_name(card_colour.strip()))
                                card.colours.add(colour_obj)

                            card.save()
        call_command('assign_existing_card_images')
