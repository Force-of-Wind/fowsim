import json
import re

from django.core.management.base import BaseCommand
from django.core.management import call_command

from fowsim import constants as CONS
from cardDatabase.models.CardType import Card, AbilityText, Race, Type, CardColour, CardAbility
from cardDatabase.models.DeckList import DeckListZone
from cardDatabase.forms import AdvancedSearchForm
from cardDatabase.views import get_set_query, sort_cards


class Command(BaseCommand):
    help = 'exports database data to a json file equivalent to what is used in importjson'

    def handle(self, *args, **options):
        output = {'fow': {
            'clusters': []
        }}
        for cluster in CONS.SET_DATA['clusters']:
            cluster_data = {"name": cluster['name'], "sets": []}
            for set in cluster['sets']:
                code = set['code']
                set_data = {
                                'name': set['name'],
                                'code': code,
                                'cards': []
                            }
                set_query = get_set_query([code])
                cards = sort_cards(Card.objects.filter(set_query).distinct(), CONS.DATABASE_SORT_BY_MOST_RECENT, False)

                for card in cards:
                    card_data = {
                        "id": card.card_id,
                        "name": card.name,
                        "type": [],
                        "race": [],
                        "cost": card.cost,
                        "colour": [],
                        "ATK": card.ATK or "",
                        "DEF": card.DEF or "",
                        "abilities": [],
                        "divinity": card.divinity or "",
                        "flavour": card.flavour or "",
                        "artists":[],
                        "rarity": card.rarity
                    }
                    for type in card.types.all():
                        card_data['type'].append(type.name)

                    for race in card.races.all():
                        card_data['race'].append(race.name)

                    for colour in card.colours.all():
                        card_data['colour'].append(colour.db_representation)

                    for ability in card.ability_texts.all():
                        card_data['abilities'].append(ability.text)

                    set_data['cards'].append(card_data)
                cluster_data['sets'].append(set_data)
            output['fow']['clusters'].append(cluster_data)

            with open('exportedCards.json', 'w') as fp:
                json.dump(output, fp)