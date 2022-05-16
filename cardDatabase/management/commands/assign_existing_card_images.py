import os

from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage

from cardDatabase.models.CardType import Card
from fowsim import constants as CONS

class Command(BaseCommand):
    help = 'Associates cards in the database with images in the MEDIA_ROOT based on ID.'
    
    def handle(self, *args, **kwargs):
        models = Card.objects.all()

        for card in models:
            try:
                card_image_path = os.path.join('cards', f'{card.card_id}.jpg')
                if default_storage.exists(card_image_path):
                    card.card_image = card_image_path
                else:
                    second_attempt = card_image_path.replace('^', '')
                    if default_storage.exists(second_attempt):
                        card.card_image = second_attempt
                    else:
                        raise Exception(f'image for {card.set_code}: {card.name} does not exist')
                card.save()
            except Exception as e:
                print(e)
                print('Failed, image doesn\'t exist?')