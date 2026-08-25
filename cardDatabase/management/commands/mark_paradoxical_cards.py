"""
Marks existing prod cards as Paradoxical by attaching the ``Paradoxical`` ``Type`` to every
card whose JSON ``type`` array contains ``"Paradoxical"``.

The card JSON is the source of truth (see implementation-plan.md §8c). This is a narrow
type-attach pass: it only touches the ``types`` M2M (not card text/images), and the
``m2m_changed`` signal recomputes ``grouping_key``/``display_name`` as the type is added.

Cards not yet present in the DB are skipped (they'll get the type when added via Add Card or
a future import).

Usage:
    python manage.py mark_paradoxical_cards            # dry-run
    python manage.py mark_paradoxical_cards --commit   # apply
"""

import json

from django.core.management.base import BaseCommand
from django.db import transaction

from fowsim import constants as CONS
from cardDatabase.models.CardType import Card, Type


class Command(BaseCommand):
    help = "Attaches the Paradoxical Type to existing cards flagged Paradoxical in the card JSON."

    def add_arguments(self, parser):
        parser.add_argument(
            "--json-path",
            default="cardDatabase/static/cards.json",
            help="Path to the card JSON (defaults to the importjson source).",
        )
        parser.add_argument(
            "--commit",
            action="store_true",
            help="Actually attach the type. Without this the command is a dry-run.",
        )

    def handle(self, *args, **options):
        commit = options["commit"]
        if not commit:
            self.stdout.write(self.style.WARNING("DRY-RUN: no changes will be written (pass --commit to write).\n"))

        with open(options["json_path"], encoding="utf-8") as json_file:
            data = json.load(json_file)

        # Collect every card_id flagged Paradoxical in the JSON.
        paradoxical_ids = []
        for cluster in data["fow"]["clusters"]:
            for fow_set in cluster["sets"]:
                for card in fow_set["cards"]:
                    if CONS.CARD_TYPE_PARADOXICAL in card.get("type", []):
                        # importjson normalises "*" in card ids to the double-sided character.
                        paradoxical_ids.append(card["id"].replace("*", CONS.DOUBLE_SIDED_CARD_CHARACTER))

        self.stdout.write(f"{len(paradoxical_ids)} card(s) flagged Paradoxical in the JSON.\n")

        to_mark = []
        skipped = []
        for card_id in paradoxical_ids:
            card = Card.objects.filter(card_id=card_id).first()
            if card is None:
                skipped.append(card_id)
                continue
            if card.is_paradoxical:
                continue  # already marked, idempotent
            to_mark.append(card)

        for card in to_mark:
            self.stdout.write(f"  - {card.card_id} '{card.name}'")
        if skipped:
            self.stdout.write(self.style.WARNING(f"\nSkipping {len(skipped)} card(s) not yet in DB: {skipped}"))

        if not commit:
            self.stdout.write(self.style.WARNING(f"\nDry-run: would mark {len(to_mark)} card(s). Re-run with --commit."))
            return

        paradoxical_type, _ = Type.objects.get_or_create(name=CONS.CARD_TYPE_PARADOXICAL)
        with transaction.atomic():
            for card in to_mark:
                card.types.add(paradoxical_type)  # m2m_changed recomputes grouping_key/display_name
        self.stdout.write(self.style.SUCCESS(f"\nMarked {len(to_mark)} card(s) as Paradoxical."))
