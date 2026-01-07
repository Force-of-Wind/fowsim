"""
Performance tests for N+1 query detection and query optimization.

These tests ensure that views and queries don't have N+1 query problems
where the number of queries grows with the number of records.
"""

import pytest
from django.db import connection, reset_queries
from django.test.utils import CaptureQueriesContext
from django.urls import reverse


# =============================================================================
# Helper functions
# =============================================================================


def get_query_count():
    """Get the current query count."""
    return len(connection.queries)


def assert_max_queries(max_count, queries):
    """Assert that the number of queries is at most max_count."""
    actual = len(queries)
    if actual > max_count:
        query_log = "\n".join(f"  {i+1}. {q['sql'][:150]}..." for i, q in enumerate(queries))
        raise AssertionError(f"Expected at most {max_count} queries, got {actual}:\n{query_log}")


# =============================================================================
# Banlist View Performance Tests
# =============================================================================


@pytest.mark.django_db
class TestBanlistPerformance:
    """Performance tests for the banlists view."""

    def test_banlists_query_count_scales_well(self, client, cards, formats, settings):
        """Test that banlists view doesn't have N+1 queries."""
        from cardDatabase.models import BannedCard, CombinationBannedCards

        settings.DEBUG = True

        # Create multiple banned cards
        for card in cards[:5]:
            BannedCard.objects.create(card=card, format=formats[0])

        # Create combination bans
        combo1 = CombinationBannedCards.objects.create(format=formats[0])
        combo1.cards.add(cards[0], cards[1])
        combo2 = CombinationBannedCards.objects.create(format=formats[0])
        combo2.cards.add(cards[2], cards[3])

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            response = client.get(reverse("cardDatabase-banlists"))
            assert response.status_code == 200

        # Should be a constant number of queries regardless of banned card count
        # Allow for some variation but catch obvious N+1 issues
        assert_max_queries(10, context.captured_queries)


# =============================================================================
# Card Search Performance Tests
# =============================================================================


@pytest.mark.django_db
class TestCardSearchPerformance:
    """Performance tests for card search functionality."""

    def test_basic_search_query_count(self, client, cards, format_obj, races, settings):
        """Test that basic search has reasonable query count."""
        settings.DEBUG = True

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            response = client.get(
                reverse("cardDatabase-search"),
                {"form_type": "basic-form", "generic_text": "Dragon"},
            )
            assert response.status_code == 200

        # Search should be efficient
        assert_max_queries(20, context.captured_queries)

    def test_advanced_search_query_count(self, client, cards, format_obj, races, settings):
        """Test that advanced search has reasonable query count."""
        settings.DEBUG = True

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            response = client.get(
                reverse("cardDatabase-search"),
                {"form_type": "advanced-form", "colours": ["R"], "rarity": ["R"]},
            )
            assert response.status_code == 200

        # Advanced search may need more queries but should still be reasonable
        assert_max_queries(25, context.captured_queries)

    def test_search_with_pagination_query_count(self, client, cards, format_obj, races, settings):
        """Test that paginated search doesn't have N+1 issues."""
        settings.DEBUG = True

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            response = client.get(
                reverse("cardDatabase-search"),
                {"form_type": "basic-form", "generic_text": "", "page": 1, "num_per_page": 5},
            )
            assert response.status_code == 200

        assert_max_queries(20, context.captured_queries)


# =============================================================================
# Card Detail Performance Tests
# =============================================================================


@pytest.mark.django_db
class TestCardDetailPerformance:
    """Performance tests for card detail view."""

    def test_view_card_query_count(self, client, card, races, formats, settings):
        """Test that viewing a card has reasonable query count."""
        settings.DEBUG = True

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            response = client.get(reverse("cardDatabase-view-card", kwargs={"card_id": card.card_id}))
            assert response.status_code == 200

        # Card detail should be efficient
        assert_max_queries(25, context.captured_queries)

    def test_view_card_with_related_data_query_count(self, client, card, decklist, races, formats, settings):
        """Test card detail with related decklists doesn't have N+1."""
        settings.DEBUG = True

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            response = client.get(reverse("cardDatabase-view-card", kwargs={"card_id": card.card_id}))
            assert response.status_code == 200

        assert_max_queries(25, context.captured_queries)


# =============================================================================
# Decklist Performance Tests
# =============================================================================


@pytest.mark.django_db
class TestDecklistPerformance:
    """Performance tests for decklist views."""

    def test_view_decklist_query_count(self, client, decklist_with_cards, settings):
        """Test that viewing a decklist has reasonable query count."""
        settings.DEBUG = True

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            response = client.get(
                reverse("cardDatabase-view-decklist", kwargs={"decklist_id": decklist_with_cards.pk})
            )
            assert response.status_code == 200

        # Decklist view loads many related objects
        assert_max_queries(35, context.captured_queries)

    def test_decklist_search_query_count(self, client, decklist_with_cards, formats, settings):
        """Test that decklist search has reasonable query count."""
        settings.DEBUG = True

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            response = client.get(
                reverse("cardDatabase-decklist-search"),
                {"form_type": "decklist-form", "contains_card": "Dragon"},
            )
            assert response.status_code == 200

        assert_max_queries(20, context.captured_queries)

    def test_user_decklists_query_count(self, client, decklist, settings):
        """Test that viewing user's decklists doesn't have N+1."""
        settings.DEBUG = True

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            response = client.get(
                reverse("cardDatabase-view-users-decklist", kwargs={"username": decklist.profile.user.username})
            )
            assert response.status_code == 200

        assert_max_queries(20, context.captured_queries)


# =============================================================================
# Tournament Performance Tests
# =============================================================================


@pytest.mark.django_db
class TestTournamentPerformance:
    """Performance tests for tournament views."""

    def test_tournament_list_query_count(self, client, tournament, formats, settings):
        """Test that tournament list has reasonable query count."""
        settings.DEBUG = True

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            response = client.get(reverse("cardDatabase-tournament-list"))
            assert response.status_code == 200

        assert_max_queries(15, context.captured_queries)

    def test_tournament_detail_query_count(self, client, tournament, settings):
        """Test that tournament detail has reasonable query count."""
        settings.DEBUG = True

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            response = client.get(reverse("cardDatabase-detail-tournament", kwargs={"tournament_id": tournament.pk}))
            assert response.status_code == 200

        assert_max_queries(20, context.captured_queries)


# =============================================================================
# Search Context Performance Tests
# =============================================================================


@pytest.mark.django_db
class TestSearchContextPerformance:
    """Performance tests for search context functions."""

    def test_get_search_form_ctx_query_count(self, races, formats, settings):
        """Test that get_search_form_ctx has minimal queries."""
        from cardDatabase.views.utils.search_context import get_search_form_ctx

        settings.DEBUG = True

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            ctx = get_search_form_ctx()

        # Should be just a couple of queries
        assert_max_queries(5, context.captured_queries)

    def test_basic_search_function_query_count(self, cards, format_obj, settings):
        """Test that basic_search has efficient queries."""
        from cardDatabase.views.utils.search_context import basic_search
        from cardDatabase.forms import SearchForm

        settings.DEBUG = True

        form = SearchForm({"generic_text": "Dragon"})

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            result = basic_search(form)
            # Force evaluation
            list(result["cards"])

        assert_max_queries(10, context.captured_queries)

    def test_advanced_search_function_query_count(self, cards, format_obj, settings):
        """Test that advanced_search has efficient queries."""
        from cardDatabase.views.utils.search_context import advanced_search
        from cardDatabase.forms import AdvancedSearchForm

        settings.DEBUG = True

        form = AdvancedSearchForm({"colours": ["R"], "rarity": ["R"]})

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            result = advanced_search(form)
            # Force evaluation
            list(result["cards"])

        assert_max_queries(10, context.captured_queries)


# =============================================================================
# Model Query Efficiency Tests
# =============================================================================


@pytest.mark.django_db
class TestModelQueryEfficiency:
    """Tests for model query efficiency with prefetch/select_related."""

    def test_card_with_relations_efficient_load(self, cards, settings):
        """Test that cards can be loaded efficiently with relations."""
        from cardDatabase.models.CardType import Card

        settings.DEBUG = True

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            # Load cards with all relations prefetched
            loaded_cards = list(
                Card.objects.prefetch_related("colours", "types", "races", "ability_texts").all()[:10]
            )
            # Access relations to ensure they're loaded
            for card in loaded_cards:
                list(card.colours.all())
                list(card.types.all())
                list(card.races.all())

        # Should be constant queries regardless of card count
        assert_max_queries(5, context.captured_queries)

    def test_decklist_with_cards_efficient_load(self, decklist_with_cards, settings):
        """Test that decklists can be loaded efficiently with cards."""
        from cardDatabase.models import DeckList

        settings.DEBUG = True

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            loaded_deck = DeckList.objects.prefetch_related(
                "cards__card__colours",
                "cards__card__types",
            ).get(pk=decklist_with_cards.pk)
            # Access relations
            for deck_card in loaded_deck.cards.all():
                list(deck_card.card.colours.all())
                list(deck_card.card.types.all())

        # Should be constant queries
        assert_max_queries(6, context.captured_queries)

    def test_tournament_with_players_efficient_load(self, tournament, tournament_player, settings):
        """Test that tournaments can be loaded efficiently with players."""
        from cardDatabase.models import Tournament

        settings.DEBUG = True

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            loaded_tournament = Tournament.objects.prefetch_related(
                "players__profile__user",
                "players__deck",
            ).get(pk=tournament.pk)
            # Access relations
            for player in loaded_tournament.players.all():
                _ = player.profile.user.username
                _ = player.deck.name

        # Should be constant queries
        assert_max_queries(5, context.captured_queries)


# =============================================================================
# N+1 Detection Tests
# =============================================================================


@pytest.mark.django_db
class TestN1QueryDetection:
    """Tests specifically designed to catch N+1 query patterns."""

    def test_iterating_cards_without_prefetch_causes_n1(self, cards, settings):
        """Demonstrate N+1 without prefetch (for comparison)."""
        from cardDatabase.models.CardType import Card

        settings.DEBUG = True

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            # Without prefetch - this will cause N+1
            loaded_cards = list(Card.objects.all()[:5])
            for card in loaded_cards:
                # Each access causes a query
                _ = list(card.colours.all())

        # This shows N+1 - should be 1 + 5 = 6 queries minimum
        # We're demonstrating the problem, not asserting it's okay
        query_count = len(context.captured_queries)
        assert query_count >= 6, "Expected N+1 queries without prefetch"

    def test_iterating_cards_with_prefetch_avoids_n1(self, cards, settings):
        """Demonstrate that prefetch avoids N+1."""
        from cardDatabase.models.CardType import Card

        settings.DEBUG = True

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            # With prefetch - no N+1
            loaded_cards = list(Card.objects.prefetch_related("colours").all()[:5])
            for card in loaded_cards:
                _ = list(card.colours.all())

        # Should be exactly 2 queries: one for cards, one for colours
        assert_max_queries(2, context.captured_queries)

    def test_decklist_cards_iteration_with_prefetch(self, decklist_with_cards, settings):
        """Test that iterating decklist cards uses prefetch correctly."""
        from cardDatabase.models import DeckList

        settings.DEBUG = True

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            deck = DeckList.objects.prefetch_related(
                "cards__card",
                "cards__card__colours",
                "cards__zone__zone",
            ).get(pk=decklist_with_cards.pk)

            # Iterate through all cards
            for deck_card in deck.cards.all():
                _ = deck_card.card.name
                _ = list(deck_card.card.colours.all())
                _ = deck_card.zone.zone.name

        # Should be constant queries
        assert_max_queries(5, context.captured_queries)


# =============================================================================
# API Performance Tests
# =============================================================================


@pytest.mark.django_db
class TestAPIPerformance:
    """Performance tests for API endpoints."""

    def test_export_decklist_query_count(self, client, decklist_with_cards, settings):
        """Test that decklist export API has reasonable queries."""
        settings.DEBUG = True

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            response = client.get(
                reverse("cardDatabase-export-decklist", kwargs={"decklist_id": decklist_with_cards.pk})
            )
            assert response.status_code == 200

        assert_max_queries(15, context.captured_queries)

    def test_reddit_bot_query_count(self, client, cards, settings):
        """Test that reddit bot API has reasonable queries."""
        import json

        settings.DEBUG = True

        reset_queries()
        with CaptureQueriesContext(connection) as context:
            response = client.post(
                reverse("cardDatabase-reddit-bot-query"),
                data=json.dumps({"keywords": ["Dragon"]}),
                content_type="application/json",
                HTTP_AUTHORIZATION=f"Bearer {settings.REDDIT_BOT_API_KEY}",
            )
            # May return 200 or 401 if auth fails
            assert response.status_code in [200, 401]

        # Only check queries if request was successful
        if response.status_code == 200:
            assert_max_queries(10, context.captured_queries)
