from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from cardDatabase.models import DeckList


def get(request, decklist_id):
    decklist = get_object_or_404(DeckList, id=decklist_id, public=True)

    deck_name = decklist.name
    cards = []
    for deck_card in decklist.cards.all():
        other_faces = deck_card.card.other_sides
        other_face_list = []
        if other_faces is not None:
            for face in other_faces:
                card = {
                    'id': face.card_id,
                    'name': face.name,
                    'img': face.card_image.url,
                }
                other_face_list.append(card)
        oracle_text = ""
        delimiter = "\n"
        for text in deck_card.card.ability_texts.all():
            oracle_text += str(text) + str(delimiter)

        card = {
            'quantity': deck_card.quantity,
            'id': deck_card.card.card_id,
            'name': deck_card.card.name,
            'zone': deck_card.zone.zone.name,
            'img': deck_card.card.card_image.url,
            'otherFaces': other_face_list,
            'oracleText': oracle_text
        }
        cards.append(card)

    return JsonResponse({'cards': cards, 'name': deck_name})