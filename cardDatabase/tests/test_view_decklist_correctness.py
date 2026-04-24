"""
Correctness tests for the view_decklist view.

These tests verify the response context data is correct, serving as a
regression safety net for query optimization refactors.
"""

import pytest
from django.urls import reverse

from cardDatabase.models import BannedCard, CombinationBannedCards, DeckList
from cardDatabase.models.CardType import Card, Tag
from cardDatabase.models.DeckList import DeckListCard, DeckListZone, UserDeckListZone
from cardDatabase.models.Rulings import (
    ExceptionAction,
    Restriction,
    RestrictionAction,
    RestrictionException,
)
from fowsim import constants as CONS


@pytest.fixture
def tag():
    return Tag.objects.create(name="TestTag")


@pytest.fixture
def restricted_tag():
    return Tag.objects.create(name="RestrictedTag")


@pytest.fixture
def restriction_action():
    return RestrictionAction.objects.create(name="Limit", technical_name="limit")


@pytest.fixture
def deck_with_all_features(profile, formats, cards, decklist_zones, tag, restricted_tag, restriction_action):
    """
    Create a deck that exercises every code path in view_decklist:
    - Multiple zones with cards
    - A banned card present in the deck
    - A combination ban where both cards are in the deck
    - A restriction with an exception
    - Cards with tags
    - Cards with other sides (Ruler / J-Ruler pair)
    """
    wanderer = formats[0]  # Wanderer

    deck = DeckList.objects.create(
        profile=profile,
        name="Full Feature Deck",
        public=True,
        deck_format=wanderer,
        comments="Test comments",
    )

    # Create user zones
    user_zones = {}
    for i, zone in enumerate(decklist_zones):
        uz = UserDeckListZone.objects.create(decklist=deck, zone=zone, position=i)
        user_zones[zone.name] = uz

    # Add cards to deck
    # cards[0] = Fire Dragon (TST-001), cards[1] = Water Spirit (TST-002), etc.
    # cards[7] = Test Ruler (TST-100), cards[8] = Test J-Ruler (TST-100J) -- other_sides pair
    # cards[9] = Basic Stone (TST-101)
    position = 1
    for card in cards:
        if "Ruler" in card.name:
            zone = user_zones["Ruler Area"]
            qty = 1
        elif "Stone" in card.name:
            zone = user_zones["Magic Stone Deck"]
            qty = 4
        elif card == cards[4]:  # Dark Vampire -> side deck
            zone = user_zones["Side Deck"]
            qty = 2
        else:
            zone = user_zones["Main Deck"]
            qty = 4

        DeckListCard.objects.create(decklist=deck, card=card, position=position, zone=zone, quantity=qty)
        position += 1

    # Add tags to some cards
    cards[0].tag.add(tag)
    cards[1].tag.add(tag)

    # Create a banned card (Fire Dragon is banned in Wanderer)
    BannedCard.objects.create(card=cards[0], format=wanderer)

    # Create a combination ban (Water Spirit + Wind Fairy)
    combo = CombinationBannedCards.objects.create(format=wanderer)
    combo.cards.add(cards[1], cards[2])

    # Create a restriction with exception
    restriction = Restriction.objects.create(
        tag=tag,
        restricted_tag=restricted_tag,
        action=restriction_action,
        text="TestTag limits RestrictedTag",
    )
    exception_action = ExceptionAction.objects.create(name="Allow", technical_name="allow")
    exception_action.applying_to_cards.add(cards[3])  # Light Knight
    RestrictionException.objects.create(
        restriction=restriction,
        exception_applying_card=cards[0],  # Fire Dragon
        card_zone_restriction="Main Deck",
        exception_action=exception_action,
    )

    return deck


@pytest.mark.django_db
class TestViewDecklistCorrectness:
    """Verify all context data returned by view_decklist is correct."""

    def _get_response(self, client, deck_id):
        url = reverse("cardDatabase-view-decklist", kwargs={"decklist_id": deck_id})
        response = client.get(url)
        assert response.status_code == 200
        return response

    def test_decklist_context(self, client, deck_with_all_features):
        """The decklist object is passed correctly."""
        response = self._get_response(client, deck_with_all_features.pk)
        assert response.context["decklist"].pk == deck_with_all_features.pk
        assert response.context["decklist"].name == "Full Feature Deck"
        assert response.context["decklist"].deck_format.name == "Wanderer"
        assert response.context["decklist"].profile.user.username == "testuser"

    def test_zones_context(self, client, deck_with_all_features):
        """All zones used by the deck appear in order."""
        response = self._get_response(client, deck_with_all_features.pk)
        zones = list(response.context["zones"])
        # Zones should be ordered by position
        assert "Ruler Area" in zones
        assert "Main Deck" in zones
        assert "Magic Stone Deck" in zones
        assert "Side Deck" in zones
        assert zones.index("Ruler Area") < zones.index("Main Deck")

    def test_cards_context(self, client, deck_with_all_features, cards):
        """All deck cards are present with correct attributes."""
        response = self._get_response(client, deck_with_all_features.pk)
        ctx_cards = response.context["cards"]
        # Should have all 10 cards
        assert len(ctx_cards) == 10

        # Verify each card has accessible attributes (no lazy load errors)
        for deck_card in ctx_cards:
            assert deck_card.card.name  # card FK resolved
            assert deck_card.zone.zone.name  # zone -> DeckListZone resolved
            assert deck_card.quantity >= 1

    def test_cards_data_context(self, client, deck_with_all_features, cards):
        """cardsData JSON structure is correct for each card."""
        response = self._get_response(client, deck_with_all_features.pk)
        cards_data = response.context["cardsData"]
        assert len(cards_data) == 10

        for entry in cards_data:
            assert "quantity" in entry
            assert "tags" in entry
            assert "id" in entry
            assert "zone" in entry
            assert isinstance(entry["tags"], list)

        # Cards with tags should have tag IDs
        tagged_entries = [e for e in cards_data if len(e["tags"]) > 0]
        assert len(tagged_entries) >= 2  # Fire Dragon and Water Spirit have tags

    def test_ban_warnings(self, client, deck_with_all_features):
        """Banned cards in the deck produce warnings."""
        response = self._get_response(client, deck_with_all_features.pk)
        ban_warnings = response.context["ban_warnings"]
        assert len(ban_warnings) == 1
        assert ban_warnings[0]["card"] == "Fire Dragon"
        assert ban_warnings[0]["format"] == "Wanderer"
        assert "view_card_url" in ban_warnings[0]
        assert "card_img_url" in ban_warnings[0]

    def test_combination_ban_warnings(self, client, deck_with_all_features):
        """Combination bans trigger when both cards are in the deck."""
        response = self._get_response(client, deck_with_all_features.pk)
        combo_warnings = response.context["combination_ban_warnings"]
        assert len(combo_warnings) == 1
        warning = combo_warnings[0]
        assert warning["format"] == "Wanderer"
        card_names = {c["name"] for c in warning["cards"]}
        assert card_names == {"Water Spirit", "Wind Fairy"}

    def test_restrictions_context(self, client, deck_with_all_features, tag, restricted_tag):
        """Restrictions and their exceptions are loaded correctly."""
        response = self._get_response(client, deck_with_all_features.pk)
        restrictions = response.context["deckRestrictions"]
        assert len(restrictions) >= 1

        restriction = restrictions[0]
        assert restriction["text"] == "TestTag limits RestrictedTag"
        assert restriction["action"] == "limit"
        assert restriction["checkingTag"] == tag.id
        assert restriction["restrictedTag"] == restricted_tag.id

        # Exception data
        assert len(restriction["exceptions"]) == 1
        exc = restriction["exceptions"][0]
        assert exc["exceptionApplyingZone"] == "Main Deck"
        assert exc["exceptionAction"] == "allow"
        assert len(exc["cardExceptionAppliesTo"]) == 1  # Light Knight

    def test_other_sides(self, client, deck_with_all_features, cards):
        """Other sides are batch-computed correctly for Ruler/J-Ruler pairs."""
        response = self._get_response(client, deck_with_all_features.pk)
        other_sides_map = response.context["other_sides_map"]

        # cards[7] = Test Ruler (TST-100) should have J-Ruler (TST-100J) as other side
        ruler = cards[7]
        assert ruler.card_id == "TST-100"
        ruler_other_side_ids = [c.card_id for c in other_sides_map.get(ruler.id, [])]
        assert "TST-100J" in ruler_other_side_ids

        # cards[8] = Test J-Ruler (TST-100J) should have Ruler (TST-100) as other side
        jruler = cards[8]
        assert jruler.card_id == "TST-100J"
        jruler_other_side_ids = [c.card_id for c in other_sides_map.get(jruler.id, [])]
        assert "TST-100" in jruler_other_side_ids

    def test_share_and_lock_defaults(self, client, deck_with_all_features):
        """Default share/lock state for a public deck with no share code."""
        response = self._get_response(client, deck_with_all_features.pk)
        assert response.context["absoluteShareLink"] is None
        # shareMode defaults to "" which is not None and not "private", so user-managed is False
        assert response.context["deckShareUserManaged"] is False
        assert response.context["deckLockUserManaged"] is True
        assert response.context["deckTournamentLocked"] is False
        assert response.context["tournamentDeck"] is False

    def test_private_deck_with_share_code(self, client, profile, formats, cards, decklist_zones):
        """Private deck with share code returns absoluteShareLink."""
        wanderer = formats[0]
        deck = DeckList.objects.create(
            profile=profile,
            name="Private Shared Deck",
            public=False,
            shareCode="abc123",
            deck_format=wanderer,
        )
        uz = UserDeckListZone.objects.create(decklist=deck, zone=decklist_zones[1], position=0)
        DeckListCard.objects.create(decklist=deck, card=cards[0], position=1, zone=uz, quantity=1)

        url = reverse(
            "cardDatabase-view-decklist-share",
            kwargs={"decklist_id": deck.pk, "share_parameter": "abc123"},
        )
        response = client.get(url)
        assert response.status_code == 200
        assert response.context["absoluteShareLink"] is not None
        assert "abc123" in response.context["absoluteShareLink"]

    def test_no_combination_ban_warning_with_only_one_card(self, client, profile, formats, cards, decklist_zones):
        """Combination ban should NOT warn if only one of the banned cards is in the deck."""
        wanderer = formats[0]
        deck = DeckList.objects.create(
            profile=profile, name="Partial Ban Deck", public=True, deck_format=wanderer,
        )
        uz = UserDeckListZone.objects.create(decklist=deck, zone=decklist_zones[1], position=0)
        # Only add cards[1] (Water Spirit), not cards[2] (Wind Fairy)
        DeckListCard.objects.create(decklist=deck, card=cards[1], position=1, zone=uz, quantity=4)

        # Create combination ban on cards[1] + cards[2]
        combo = CombinationBannedCards.objects.create(format=wanderer)
        combo.cards.add(cards[1], cards[2])

        response = self._get_response(client, deck.pk)
        assert len(response.context["combination_ban_warnings"]) == 0

    def test_cards_without_other_sides(self, client, profile, formats, decklist_zones, card_colour, card_type):
        """Cards with no other sides should have empty list in other_sides_map."""
        wanderer = formats[0]
        solo_card = Card.objects.create(
            name="Solo Card", name_without_punctuation="Solo Card", card_id="SOL-001",
            cost="{1}{R}", rarity="C",
        )
        solo_card.colours.add(card_colour)
        solo_card.types.add(card_type)

        deck = DeckList.objects.create(
            profile=profile, name="Solo Deck", public=True, deck_format=wanderer,
        )
        uz = UserDeckListZone.objects.create(decklist=deck, zone=decklist_zones[1], position=0)
        DeckListCard.objects.create(decklist=deck, card=solo_card, position=1, zone=uz, quantity=1)

        response = self._get_response(client, deck.pk)
        other_sides_map = response.context["other_sides_map"]
        assert other_sides_map.get(solo_card.id) == []
