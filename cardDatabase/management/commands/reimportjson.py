from django.core.management.base import BaseCommand
from django.core.management import call_command

from cardDatabase.models.CardType import Card


class Command(BaseCommand):
    help = 'Deletes all Card objects and runs importjson.py'

    def handle(self, *args, **options):
        print(f'Deleting {Card.objects.all().count()} cards')
        Card.objects.all().delete()
        print('Running importjson')
        call_command('importjson')