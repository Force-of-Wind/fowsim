import datetime

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from fowsim import constants as CONS
from cardDatabase.models.Tournament import Tournament


class Command(BaseCommand):
    help = (
        f"Closes tournaments that started more than {CONS.TOURNAMENT_AUTO_CLOSE_DAYS} days ago and have "
        "not been completed yet by setting their phase to 'completed'. Intended to be run on a schedule "
        "(e.g. daily) so stale events do not linger in an open phase when staff forget to close them."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=CONS.TOURNAMENT_AUTO_CLOSE_DAYS,
            help="Number of days after the start date before a tournament is auto-closed.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List the tournaments that would be closed without modifying anything.",
        )

    def handle(self, *args, **options):
        days = options["days"]
        dry_run = options["dry_run"]

        cutoff = timezone.now() - datetime.timedelta(days=days)

        expired = Tournament.objects.filter(
            ~Q(phase=CONS.TOURNAMENT_PHASE_COMPLETED),
            start_datetime__lt=cutoff,
        )

        count = expired.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS("No expired tournaments to close."))
            return

        for tournament in expired:
            self.stdout.write(
                f"{'[dry-run] ' if dry_run else ''}Closing '{tournament.title}' "
                f"(id={tournament.pk}, phase='{tournament.phase}', started {tournament.start_datetime:%Y-%m-%d})"
            )

        if dry_run:
            self.stdout.write(self.style.WARNING(f"Dry run: {count} tournament(s) would be closed."))
            return

        updated = expired.update(phase=CONS.TOURNAMENT_PHASE_COMPLETED)
        self.stdout.write(self.style.SUCCESS(f"Closed {updated} expired tournament(s)."))
