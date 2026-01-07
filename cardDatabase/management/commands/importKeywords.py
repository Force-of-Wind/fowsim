from django.core.management.base import BaseCommand

from cardDatabase.models.Ability import Keyword
from fowsim import constants as CONS


class Command(BaseCommand):
    help = "Creates all Keyword objects in the database if they dont already exist"

    def handle(self, *args, **options):
        for search_string, name in CONS.KEYWORDS_CHOICES:
            Keyword.objects.get_or_create(search_string=search_string, name=name)
