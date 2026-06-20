"""
Tests for the AddCardForm paradoxical/modal handling and the add-card page rendering.
"""

import pytest
from django.urls import reverse

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


def _base_form_data(card_colour, types):
    return {
        "name": "Placeholder",
        "card_id": "ADD-000",
        "rarity": "R",
        "types": [t.pk for t in types],
        "colours": [card_colour.pk],
        "races": "",
        "artists": "",
        "ability_texts": "",
        "flavour": "",
        "cost": "",
        "divinity": "",
        "will_power": "",
        "modal_face": "",
        "modal_partner": "",
    }


@pytest.mark.django_db
class TestAddCardForm:
    def test_paradoxical_type_marks_grouping_key(self, card_colour, card_type, paradoxical_type):
        from cardDatabase.forms import AddCardForm

        data = _base_form_data(card_colour, [card_type, paradoxical_type])
        data["name"] = "Echo"
        data["card_id"] = "ADD-001"

        form = AddCardForm(data)
        assert form.is_valid(), form.errors
        card = form.save()
        form.save_m2m()
        card.refresh_from_db()

        assert card.is_paradoxical
        assert card.grouping_key == f"Echo{CONS.GROUPING_KEY_SEPARATOR}PARADOXICAL"
        assert card.display_name == "Echo (Paradoxical)"

    def test_modal_fields_link_both_halves(self, card_colour, card_type):
        from cardDatabase.forms import AddCardForm

        bottom = _make_card(
            "Bottom", "ADD-010" + CONS.DOUBLE_SIDED_CARD_CHARACTER, card_colour, [card_type]
        )

        data = _base_form_data(card_colour, [card_type])
        data["name"] = "Top"
        data["card_id"] = "ADD-010"
        data["modal_face"] = CONS.MODAL_FACE_TOP
        data["modal_partner"] = bottom.card_id

        form = AddCardForm(data)
        assert form.is_valid(), form.errors
        top = form.save()
        form.save_m2m()
        top.refresh_from_db()
        bottom.refresh_from_db()

        assert top.modal_face == CONS.MODAL_FACE_TOP
        assert top.modal_partner_id == bottom.id
        assert bottom.modal_face == CONS.MODAL_FACE_BOTTOM
        assert bottom.modal_partner_id == top.id

        combined = "Top//Bottom"
        assert top.grouping_key == combined
        assert bottom.grouping_key == combined

    def test_modal_face_without_partner_invalid(self, card_colour, card_type):
        from cardDatabase.forms import AddCardForm

        data = _base_form_data(card_colour, [card_type])
        data["name"] = "Lonely"
        data["card_id"] = "ADD-020"
        data["modal_face"] = CONS.MODAL_FACE_TOP

        form = AddCardForm(data)
        assert not form.is_valid()
        assert "modal_partner" in form.errors

    def test_form_renders_with_paradoxical_type(self, card_type, paradoxical_type):
        # AddCardForm.__init__ sorts the type checkboxes via DATABASE_CARD_TYPE_GROUPS.index().
        # A Type present in the DB but absent from the groups list raises ValueError and breaks
        # the add-card page - so instantiating + rendering the form must succeed with Paradoxical
        # present.
        from cardDatabase.forms import AddCardForm

        form = AddCardForm()  # would raise ValueError if Paradoxical weren't in the groups list
        rendered = str(form["types"])
        assert "Paradoxical" in rendered

    def test_form_renders_with_type_absent_from_groups(self, card_type):
        # A Type present in the DB but absent from DATABASE_CARD_TYPE_GROUPS (e.g. the legacy
        # "Chant/Master Rune") must not raise ValueError in the add-card type sort.
        from cardDatabase.forms import AddCardForm
        from cardDatabase.models.CardType import Type

        Type.objects.create(name="Chant/Master Rune")

        form = AddCardForm()  # must not raise
        choices = list(form["types"].field.widget.choices)
        # Unknown type sorts to the end rather than breaking the page.
        assert any("Chant/Master Rune" in str(c[1]) for c in choices)
