import os

from django.core.management.base import BaseCommand
from cardDatabase.models.CardType import Card

from fowsim import constants as CONS

class Command(BaseCommand):
    help = 'Associates cards in the database with images in the MEDIA_ROOT based on ID.'
    
    def handle(self, *args, **kwargs):
        models = Card.objects.all()

        for card in models:
            try:
                print(f'Trying to add image for {card.card_id}... ', end='')
                card_image_path = os.path.join('cards', f'{card.card_id}.jpg')
                card.card_image = card_image_path
                card.save(use_resize=False)
                print('Success!')
            except:
                print('Failed, image doesn\'t exist?')