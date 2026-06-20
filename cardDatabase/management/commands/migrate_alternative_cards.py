"""
One-off migration that extracts the *alternative* card pairs out of the legacy ``^``/``*``
two-sided pool and wires them up with explicit alternative modelling (``alternative_face`` /
``alternative_partner``).

`other_sides` is NOT removed or repurposed: genuine two-sided / transform cards share the
same ``^``/``*`` pool, so alternative pairs must be named explicitly (never inferred from card
type). See implementation-plan.md §4.

Usage:
    # Report every ^/* candidate pair for human review (no writes):
    python manage.py migrate_alternative_cards --report

    # Dry-run marking a curated list of alternative *top-half* base card_ids (no writes):
    python manage.py migrate_alternative_cards --alternative-ids XXX-064 YYY-012

    # Same, but read the base ids from a committed fixture:
    python manage.py migrate_alternative_cards --alternative-file cardDatabase/static/alternative_cards.json

    # Actually write the marks:
    python manage.py migrate_alternative_cards --alternative-ids XXX-064 --commit

    # Recompute grouping_key/display_name for the whole table:
    python manage.py migrate_alternative_cards --backfill-all --commit
"""

import json

from django.core.management.base import BaseCommand
from django.db import transaction

from fowsim import constants as CONS
from cardDatabase.models.CardType import Card


BOTTOM_SUFFIXES = [CONS.DOUBLE_SIDED_CARD_CHARACTER, CONS.ALTERNATIVE_SIDE_CHARACTER]  # "^", "*"
J_SUFFIXES = [CONS.J_SIDE_CHARACTER, CONS.COLOSSAL_SIDE_CHARACTER]  # "J", "J^"


class Command(BaseCommand):
    help = "Extracts curated alternative card pairs from the legacy ^/* two-sided pool."

    def add_arguments(self, parser):
        parser.add_argument(
            "--report",
            action="store_true",
            help="Enumerate every ^/* candidate pair for human review. No writes.",
        )
        parser.add_argument(
            "--alternative-ids",
            nargs="*",
            default=[],
            metavar="BASE_CARD_ID",
            help="Explicit list of alternative TOP-half base card_ids (e.g. XXX-064).",
        )
        parser.add_argument(
            "--alternative-file",
            default=None,
            help="Path to a JSON file containing a list of alternative TOP-half base card_ids.",
        )
        parser.add_argument(
            "--backfill-all",
            action="store_true",
            help="Recompute grouping_key/display_name for every card in the table.",
        )
        parser.add_argument(
            "--commit",
            action="store_true",
            help="Actually write changes. Without this the command is a dry-run.",
        )

    def handle(self, *args, **options):
        commit = options["commit"]
        if not commit:
            self.stdout.write(self.style.WARNING("DRY-RUN: no changes will be written (pass --commit to write).\n"))

        if options["report"]:
            self.report_candidates()
            return

        alternative_ids = list(options["alternative_ids"])
        if options["alternative_file"]:
            with open(options["alternative_file"], encoding="utf-8") as f:
                alternative_ids.extend(json.load(f))

        if alternative_ids:
            self.mark_alternative_pairs(alternative_ids, commit)

        if options["backfill_all"]:
            self.backfill_all(commit)

        if not alternative_ids and not options["backfill_all"]:
            self.stdout.write(
                "Nothing to do. Use --report, --alternative-ids/--alternative-file, or --backfill-all."
            )

    # ------------------------------------------------------------------ #
    # 1. Enumerate candidates (report only)
    # ------------------------------------------------------------------ #
    def report_candidates(self):
        self.stdout.write("Candidate ^/* pairs (review which are actually alternative vs genuine two-sided):\n")
        count = 0
        for card in Card.objects.all().order_by("card_id"):
            number = card.set_number
            if not number:
                continue
            suffix = next((s for s in BOTTOM_SUFFIXES if number.endswith(s)), None)
            if not suffix:
                continue
            base_id = card.card_id[: -len(suffix)]
            base = Card.objects.filter(card_id=base_id).first()
            count += 1
            base_desc = (
                f"{base.card_id} '{base.name}' types={[t.name for t in base.types.all()]}"
                if base
                else f"{base_id} (MISSING base row)"
            )
            self.stdout.write(
                f"  - bottom: {card.card_id} '{card.name}' types={[t.name for t in card.types.all()]}\n"
                f"      top: {base_desc}"
            )
        self.stdout.write(f"\n{count} candidate ^/* card(s) found.")

    # ------------------------------------------------------------------ #
    # 2-5. Mark the curated alternative pairs
    # ------------------------------------------------------------------ #
    def mark_alternative_pairs(self, base_ids, commit):
        self.stdout.write(f"Marking {len(base_ids)} alternative pair(s):\n")
        to_apply = []  # list of (top, bottom)

        for base_id in base_ids:
            top = Card.objects.filter(card_id=base_id).first()
            if top is None:
                self.stdout.write(self.style.ERROR(f"  ! {base_id}: no card with this card_id, skipping."))
                continue

            # Guard: refuse a card that has a J / J^ partner (ruler flip), not a alternative half.
            j_partner = next(
                (Card.objects.filter(card_id=base_id + j).first() for j in J_SUFFIXES if Card.objects.filter(card_id=base_id + j).exists()),
                None,
            )
            if j_partner is not None:
                self.stdout.write(
                    self.style.ERROR(
                        f"  ! {base_id}: has a J/J^ partner ({j_partner.card_id}); looks like a ruler flip, refusing."
                    )
                )
                continue

            bottom = None
            for suffix in BOTTOM_SUFFIXES:
                bottom = Card.objects.filter(card_id=base_id + suffix).first()
                if bottom is not None:
                    break
            if bottom is None:
                self.stdout.write(
                    self.style.ERROR(f"  ! {base_id}: no ^/* bottom-half partner found, skipping.")
                )
                continue

            self.stdout.write(f"  - top {top.card_id} '{top.name}'  <->  bottom {bottom.card_id} '{bottom.name}'")
            to_apply.append((top, bottom))

        if not commit:
            self.stdout.write(self.style.WARNING("\nDry-run: not writing. Re-run with --commit to apply."))
            return

        with transaction.atomic():
            for top, bottom in to_apply:
                top.alternative_face = Card.ALTERNATIVE_FACE_TOP
                top.alternative_partner = bottom
                bottom.alternative_face = Card.ALTERNATIVE_FACE_BOTTOM
                bottom.alternative_partner = top
                top.save()
                bottom.save()
                # Both linked now - recompute so they share the canonical "top//bottom" key.
                top.recompute_grouping(save=True)
                bottom.recompute_grouping(save=True)
        self.stdout.write(self.style.SUCCESS(f"\nMarked {len(to_apply)} alternative pair(s)."))

    # ------------------------------------------------------------------ #
    # 6. Back-fill grouping_key/display_name for the whole table
    # ------------------------------------------------------------------ #
    def backfill_all(self, commit):
        cards = Card.objects.all()
        total = cards.count()
        self.stdout.write(f"Back-filling grouping_key/display_name for {total} card(s)...")
        if not commit:
            self.stdout.write(self.style.WARNING("Dry-run: not writing. Re-run with --commit to apply."))
            return
        changed = 0
        for card in cards.iterator():
            new_key = card.compute_grouping_key()
            new_display = card.compute_display_name()
            if card.grouping_key != new_key or card.display_name != new_display:
                Card.objects.filter(pk=card.pk).update(grouping_key=new_key, display_name=new_display)
                changed += 1
        self.stdout.write(self.style.SUCCESS(f"Back-filled. {changed} card(s) updated."))
