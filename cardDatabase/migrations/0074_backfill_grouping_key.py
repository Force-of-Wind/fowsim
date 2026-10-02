"""
Back-fill grouping_key/display_name for all existing cards so the grouping-key-based
reprints/bans/rulings lookups work immediately after this migration.

At this point no card carries the Paradoxical type or alternative fields yet (those are marked by
the mark_paradoxical_cards / migrate_alternative_cards commands afterwards), so every existing card's
canonical grouping_key/display_name is simply its name. The marking commands recompute the
affected cards.
"""

from django.db import migrations
from django.db.models import F


def backfill_grouping(apps, schema_editor):
    Card = apps.get_model("cardDatabase", "Card")
    # Only touch rows that haven't been populated yet.
    Card.objects.filter(grouping_key="").update(grouping_key=F("name"), display_name=F("name"))


def clear_grouping(apps, schema_editor):
    Card = apps.get_model("cardDatabase", "Card")
    Card.objects.update(grouping_key="", display_name="")


class Migration(migrations.Migration):

    dependencies = [
        ("cardDatabase", "0073_paradoxical_type"),
    ]

    operations = [
        migrations.RunPython(backfill_grouping, clear_grouping),
    ]
