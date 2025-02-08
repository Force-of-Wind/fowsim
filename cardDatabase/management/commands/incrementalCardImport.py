import json
import re
import os
import boto3

from io import BytesIO

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.core.files.storage import default_storage
from django.conf import settings

from fowsim import constants as CONS
from cardDatabase.models.CardType import Card, AbilityText, Race, Type, CardColour, CardAbility
from cardDatabase.models.DeckList import DeckListZone


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

class Command(BaseCommand):
    help = 'imports static/cardBatchImport.json to the database from s3 bucket'

    def handle(self, *args, **options):
        s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key= settings.AWS_SECRET_ACCESS_KEY)

        content_object = s3.Object('fowsim', 'static/cardBatchImport.json')
        json_file = content_object.get()['Body'].read().decode('utf-8')
        
        data = json.loads(json_file)
        for cluster in data['fow']['clusters']:
            sets = cluster['sets']
            for fow_set in sets:
                cards = fow_set['cards']
                for card in cards:
                    for unused_set in CONS.UNSEARCHED_DATABASE_SETS:  # Mostly just old Valhalla
                        if card['id'].startswith(unused_set):
                            break
                    else:
                        #card already exists -> continue to next card
                        if Card.objects.filter(card_id=card['id']).exists():
                            continue
                        # In a used set
                        card_types = card['type']
                        card_races = card['race']
                        card_abilities = card['abilities']
                        card_colours = card['colour']
                        card, created = Card.objects.get_or_create(
                            name=replace_name_errors(card['name']),
                            name_without_punctuation=remove_punctuation(card['name']),
                            card_id=card['id'].replace('*', CONS.DOUBLE_SIDED_CARD_CHARACTER),
                            cost=card['cost'] or None,
                            divinity=str(card['divinity']).replace("∞", CONS.INFINITY_STRING) or None,
                            flavour=card['flavour'] or None,
                            rarity=card['rarity'],
                            ATK=card['ATK'] or None,
                            DEF=card['DEF'] or None,
                        )
                        position = 1
                        for card_ability in card_abilities:
                            try:
                                ability_text = AbilityText.objects.get_or_create(text=card_ability.strip())
                            except AbilityText.MultipleObjectsReturned:
                                ability_text = AbilityText.objects.filter(text=card_ability.strip()).first()

                            CardAbility.objects.get_or_create(ability_text=ability_text, card=card, position=position)
                            position += 1
                        for card_race in card_races:
                            try:
                                race = Race.objects.get_or_create(name=card_race.strip())
                            except Race.MultipleObjectsReturned:
                                race = Race.objects.filter(name=card_race.strip()).first()
                            card.races.add(race)
                        for card_type in card_types:
                            try:
                                type_obj = Type.objects.get_or_create(name=card_type.strip())
                            except Type.MultipleObjectsReturned:
                                type_obj = Type.objects.filter(name=card_type.strip()).first()
                            card.types.add(type_obj)
                        for card_colour in card_colours:
                            try:
                                colour_obj = CardColour.objects.get_or_create(db_representation=card_colour.strip(), name=get_colour_name(card_colour.strip()))
                            except:
                                colour_obj = CardColour.objects.filter(db_representation=card_colour.strip(), name=get_colour_name(card_colour.strip())).first()
                            card.colours.add(colour_obj)
                        card.save()
                        #import media for card
                        try:
                            card_image_path = os.path.join('cards', f'{card.card_id}.jpg')
                            if default_storage.exists(card_image_path):
                                card._card_image = card_image_path
                            else:
                                second_attempt = card_image_path.replace('^', '')
                                if default_storage.exists(second_attempt):
                                    card._card_image = second_attempt
                                else:
                                    raise Exception(f'image for {card.set_code}: {card.name} does not exist')
                            card.save()
                        except Exception as e:
                            print(e)
                            print('Failed, image doesn\'t exist?')