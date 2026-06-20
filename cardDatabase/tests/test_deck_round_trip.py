"""
Deck round-trip tests: same-named normal+paradoxical and standalone+modal cards form
distinct stacks, and legacy modal bottom-half references normalise to the top half on load.
"""

import pytest

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


def _linked_modal_pair(card_colour, card_type):
    top = _make_card("Split", "MOD-001", card_colour, [card_type])
    bottom = _make_card("Rabbit", "MOD-001" + CONS.DOUBLE_SIDED_CARD_CHARACTER, card_colour, [card_type])
    top.modal_face = top.MODAL_FACE_TOP
    top.modal_partner = bottom
    bottom.modal_face = bottom.MODAL_FACE_BOTTOM
    bottom.modal_partner = top
    top.save()
    bottom.save()
    top.recompute_grouping(save=True)
    bottom.recompute_grouping(save=True)
    top.refresh_from_db()
    bottom.refresh_from_db()
    return top, bottom


@pytest.mark.django_db
class TestDeckRoundTrip:
    def test_normal_and_paradoxical_are_distinct_stacks(self, card_colour, card_type, paradoxical_type):
        normal = _make_card("Twin", "DR-001", card_colour, [card_type])
        paradox = _make_card("Twin", "DR-002", card_colour, [card_type, paradoxical_type])

        # Distinct grouping keys => the deck editor keys them into separate stacks.
        assert normal.grouping_key != paradox.grouping_key

    def test_standalone_and_modal_are_distinct_stacks(self, card_colour, card_type):
        standalone = _make_card("Split", "DR-010", card_colour, [card_type])
        top, _ = _linked_modal_pair(card_colour, card_type)

        assert standalone.grouping_key != top.grouping_key

    def test_modal_bottom_half_normalises_to_top_on_load(
        self, profile, format_obj, decklist_zone, card_colour, card_type
    ):
        from cardDatabase.models import DeckList
        from cardDatabase.models.DeckList import DeckListCard, UserDeckListZone
        from cardDatabase.views.utils.search_context import normalise_modal_bottom_halves

        top, bottom = _linked_modal_pair(card_colour, card_type)

        decklist = DeckList.objects.create(
            profile=profile, name="Legacy Deck", public=True, deck_format=format_obj
        )
        user_zone = UserDeckListZone.objects.create(decklist=decklist, zone=decklist_zone, position=1)
        # Legacy reference to the bottom half.
        DeckListCard.objects.create(
            decklist=decklist, card=bottom, position=1, zone=user_zone, quantity=2
        )

        normalised = normalise_modal_bottom_halves(
            DeckListCard.objects.filter(decklist=decklist).select_related("card", "card__modal_partner")
        )
        assert len(normalised) == 1
        # Swapped to the top half representative.
        assert normalised[0].card.id == top.id
        assert normalised[0].card.grouping_key == "Split//Rabbit"
