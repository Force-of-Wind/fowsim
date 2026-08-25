"""
Tests for the migrate_alternative_cards management command.
"""

from io import StringIO

import pytest
from django.core.management import call_command

from fowsim import constants as CONS


def _make_card(name, card_id, colour, types=()):
    from cardDatabase.models.CardType import Card

    c = Card.objects.create(
        name=name,
        name_without_punctuation=name,
        card_id=card_id,
        rarity="R",
    )
    c.colours.add(colour)
    for t in types:
        c.types.add(t)
    c.refresh_from_db()
    return c


@pytest.mark.django_db
class TestMigrateAlternativeCards:
    def _alternative_pair(self, card_colour, card_type):
        top = _make_card("Split Heaven and Earth", "XXX-064", card_colour, [card_type])
        bottom = _make_card(
            "Groundsplitting Rabbit", "XXX-064" + CONS.DOUBLE_SIDED_CARD_CHARACTER, card_colour, [card_type]
        )
        return top, bottom

    def _transform_pair(self, card_colour, card_type):
        """A genuine (non-alternative) two-sided/transform pair sharing the ^ pool."""
        front = _make_card("Transform Front", "YYY-010", card_colour, [card_type])
        back = _make_card(
            "Transform Back", "YYY-010" + CONS.DOUBLE_SIDED_CARD_CHARACTER, card_colour, [card_type]
        )
        return front, back

    def test_marks_only_named_pair(self, card_colour, card_type):
        top, bottom = self._alternative_pair(card_colour, card_type)
        front, back = self._transform_pair(card_colour, card_type)

        out = StringIO()
        call_command("migrate_alternative_cards", "--alternative-ids", "XXX-064", "--commit", stdout=out)

        top.refresh_from_db()
        bottom.refresh_from_db()
        front.refresh_from_db()
        back.refresh_from_db()

        # Named pair is marked symmetrically.
        assert top.alternative_face == CONS.ALTERNATIVE_FACE_TOP
        assert top.alternative_partner_id == bottom.id
        assert bottom.alternative_face == CONS.ALTERNATIVE_FACE_BOTTOM
        assert bottom.alternative_partner_id == top.id

        combined = "Split Heaven and Earth//Groundsplitting Rabbit"
        assert top.grouping_key == combined
        assert bottom.grouping_key == combined

        # Genuine two-sided pair left untouched.
        assert front.alternative_face is None
        assert back.alternative_face is None
        assert front.grouping_key == "Transform Front"

    def test_genuine_two_sided_other_sides_unchanged(self, card_colour, card_type):
        front, back = self._transform_pair(card_colour, card_type)
        # other_sides still wires them together (it never changed).
        assert back in front.other_sides
        assert front in back.other_sides

    def test_no_op_without_commit(self, card_colour, card_type):
        top, bottom = self._alternative_pair(card_colour, card_type)

        out = StringIO()
        call_command("migrate_alternative_cards", "--alternative-ids", "XXX-064", stdout=out)

        top.refresh_from_db()
        bottom.refresh_from_db()
        assert top.alternative_face is None
        assert bottom.alternative_face is None

    def test_refuses_j_ruler_partner(self, card_colours, card_types):
        from cardDatabase.models.CardType import Card

        ruler = Card.objects.create(
            name="Some Ruler", name_without_punctuation="Some Ruler", card_id="ZZZ-100", rarity="RR"
        )
        ruler.colours.add(card_colours[0])
        ruler.types.add(card_types[4])  # Ruler
        j_ruler = Card.objects.create(
            name="Some J-Ruler", name_without_punctuation="Some J-Ruler", card_id="ZZZ-100J", rarity="JR"
        )
        j_ruler.colours.add(card_colours[0])
        j_ruler.types.add(card_types[5])  # J-Ruler

        out = StringIO()
        call_command("migrate_alternative_cards", "--alternative-ids", "ZZZ-100", "--commit", stdout=out)

        ruler.refresh_from_db()
        assert ruler.alternative_face is None
        assert "ruler flip" in out.getvalue().lower() or "refusing" in out.getvalue().lower()

    def test_backfill_all_recomputes(self, card_colour, card_type, paradoxical_type):
        from cardDatabase.models.CardType import Card

        # Create a paradoxical card but blank out its denormalised columns to simulate stale data.
        paradox = _make_card("Stale", "TST-300", card_colour, [card_type, paradoxical_type])
        Card.objects.filter(pk=paradox.pk).update(grouping_key="", display_name="")

        out = StringIO()
        call_command("migrate_alternative_cards", "--backfill-all", "--commit", stdout=out)

        paradox.refresh_from_db()
        assert paradox.grouping_key.endswith("PARADOXICAL")
        assert paradox.display_name == "Stale (Paradoxical)"
