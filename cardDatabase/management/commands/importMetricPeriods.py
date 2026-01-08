from django.core.management.base import BaseCommand

from cardDatabase.models.Metrics import PickPeriod
from fowsim.constants import PICK_PERIOD_DAYS


class Command(BaseCommand):
    help = "Imports the relevant Metrics.PickPeriod objects to the database"

    def handle(self, *args, **options):
        for num_of_days in PICK_PERIOD_DAYS:
            PickPeriod.objects.get_or_create(days=num_of_days)
        PickPeriod.objects.get_or_create(days=0, all_time=True)
