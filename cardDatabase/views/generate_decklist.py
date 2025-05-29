from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from cardDatabase.models import DeckList


def get(decklist):
    deck_name = decklist.name
    cards = []
    for deck_card in decklist.cards.all():
        other_faces = deck_card.card.other_sides
        other_face_list = []
        if other_faces is not None:  # TODO: unneeded check
            for face in other_faces:
                oracle_text = ""
                delimiter = "\n"
                for ability in face.abilities.order_by('position').all():
                    oracle_text += str(ability.ability_text) + str(delimiter)

                races = []
                for race in face.races.all():
                    races.append(race.name)

                types = []
                for type in face.types.all():
                    types.append(type.name)

                card = {
                    'id': face.card_id,
                    'name': face.name,
                    'img': face.card_image.url,
                    'cost': face.cost,
                    'races': races,
                    'types': types,
                    'ATK': face.ATK,
                    'DEF': face.DEF,
                    'oracleText': oracle_text
                }
                other_face_list.append(card)
        oracle_text = ""
        delimiter = "\n"
        for ability in deck_card.card.abilities.order_by('position').all():
            oracle_text += str(ability.ability_text) + str(delimiter)

        races = []
        for race in deck_card.card.races.all():
            races.append(race.name)

        types = []
        for type in deck_card.card.types.all():
            types.append(type.name)

        card = {
            'quantity': deck_card.quantity,
            'id': deck_card.card.card_id,
            'cost': deck_card.card.cost,
            'ATK': deck_card.card.ATK,
            'DEF': deck_card.card.DEF,
            'name': deck_card.card.name,
            'races': races,
            'types': types,
            'zone': deck_card.zone.zone.name,
            'img': deck_card.card.card_image.url,
            'otherFaces': other_face_list,
            'oracleText': oracle_text
        }
        cards.append(card)

    return JsonResponse({'cards': cards, 'name': deck_name})