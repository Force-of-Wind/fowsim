"""
Tests for the paradoxical / modal advanced-search filters and modal bottom-half exclusion.
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


@pytest.fixture
def search_world(card_colour, card_type, paradoxical_type):
    """A normal card, a paradoxical card, and a linked modal pair."""
    normal = _make_card("Plain", "SCH-001", card_colour, [card_type])
    paradox = _make_card("Echo", "SCH-002", card_colour, [card_type, paradoxical_type])
    top = _make_card("Top Name", "SCH-003", card_colour, [card_type])
    bottom = _make_card("Bottom Name", "SCH-003" + CONS.DOUBLE_SIDED_CARD_CHARACTER, card_colour, [card_type])
    top.modal_face = top.MODAL_FACE_TOP
    top.modal_partner = bottom
    bottom.modal_face = bottom.MODAL_FACE_BOTTOM
    bottom.modal_partner = top
    top.save()
    bottom.save()
    top.recompute_grouping(save=True)
    bottom.recompute_grouping(save=True)
    return {"normal": normal, "paradox": paradox, "top": top, "bottom": bottom}


def _run_advanced_search(data):
    from cardDatabase.forms import AdvancedSearchForm
    from cardDatabase.views.utils.search_context import advanced_search

    form = AdvancedSearchForm(data)
    assert form.is_valid(), form.errors
    return list(advanced_search(form)["cards"])


@pytest.mark.django_db
class TestParadoxicalModalSearch:
    def test_paradoxical_filter(self, search_world):
        results = _run_advanced_search({"paradoxical": "on"})
        assert search_world["paradox"] in results
        assert search_world["normal"] not in results
        assert search_world["top"] not in results

    def test_modal_filter(self, search_world):
        results = _run_advanced_search({"modal": "on"})
        assert search_world["top"] in results
        # Bottom half is always excluded from results.
        assert search_world["bottom"] not in results
        assert search_world["normal"] not in results

    def test_default_search_excludes_modal_bottom(self, search_world):
        results = _run_advanced_search({})
        assert search_world["normal"] in results
        assert search_world["paradox"] in results
        assert search_world["top"] in results
        assert search_world["bottom"] not in results

    def test_bottom_half_name_search_surfaces_top(self, search_world):
        # Searching the bottom half's name must still find the (addable) top half via its
        # combined display_name, even though the bottom itself is excluded from results.
        results = _run_advanced_search(
            {
                "generic_text": "Bottom Name",
                "text_search_fields": ["name"],
                "text_exactness": CONS.TEXT_CONTAINS_ALL,
            }
        )
        assert search_world["top"] in results
        assert search_world["bottom"] not in results

    def test_query_helpers(self, search_world):
        from cardDatabase.views.utils.search_context import (
            get_paradoxical_query,
            get_modal_query,
        )
        from cardDatabase.models.CardType import Card

        paradoxical = list(Card.objects.filter(get_paradoxical_query(True)).distinct())
        assert search_world["paradox"] in paradoxical
        assert search_world["normal"] not in paradoxical

        modal = list(Card.objects.filter(get_modal_query(True)).distinct())
        assert search_world["top"] in modal
        assert search_world["bottom"] in modal
        assert search_world["normal"] not in modal
