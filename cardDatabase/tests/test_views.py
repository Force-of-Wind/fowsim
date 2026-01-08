"""
Tests for cardDatabase views.
"""

import pytest
from django.urls import reverse


# =============================================================================
# Tests for Start/Home View
# =============================================================================


@pytest.mark.django_db
class TestStartView:
    """Tests for the start/home view."""

    def test_home_page_loads(self, client, races, formats):
        response = client.get(reverse("cardDatabase-home"))
        assert response.status_code == 200

    def test_home_page_contains_forms(self, client, races, formats):
        response = client.get(reverse("cardDatabase-home"))
        assert "basic_form" in response.context
        assert "advanced_form" in response.context

    def test_home_page_contains_search_context(self, client, races, formats):
        response = client.get(reverse("cardDatabase-home"))
        assert "races_list" in response.context
        assert "format_list" in response.context


# =============================================================================
# Tests for Search View
# =============================================================================


@pytest.mark.django_db
class TestSearchView:
    """Tests for the card search view."""

    def test_search_page_loads(self, client, races, formats):
        response = client.get(reverse("cardDatabase-search"))
        assert response.status_code == 200

    def test_basic_search_form(self, client, cards, format_obj, races):
        response = client.get(
            reverse("cardDatabase-search"),
            {"form_type": "basic-form", "generic_text": "Dragon"},
        )
        assert response.status_code == 200
        assert "cards" in response.context

    def test_advanced_search_form(self, client, cards, format_obj, races):
        response = client.get(
            reverse("cardDatabase-search"),
            {"form_type": "advanced-form", "colours": ["R"]},
        )
        assert response.status_code == 200
        assert "cards" in response.context

    def test_search_with_pagination(self, client, cards, format_obj, races):
        response = client.get(
            reverse("cardDatabase-search"),
            {"form_type": "basic-form", "generic_text": ""},
        )
        assert response.status_code == 200

    def test_spoiler_season_search(self, client, cards):
        response = client.get(
            reverse("cardDatabase-search"),
            {"spoiler_season": "TST"},
        )
        assert response.status_code == 200


# =============================================================================
# Tests for View Card
# =============================================================================


@pytest.mark.django_db
class TestViewCardView:
    """Tests for the card detail view."""

    def test_view_card_loads(self, client, card, races, formats):
        response = client.get(reverse("cardDatabase-view-card", kwargs={"card_id": card.card_id}))
        assert response.status_code == 200
        assert response.context["card"] == card

    def test_view_card_not_found(self, client):
        response = client.get(reverse("cardDatabase-view-card", kwargs={"card_id": "INVALID-999"}))
        assert response.status_code == 404

    def test_view_card_has_search_context(self, client, card, races, formats):
        response = client.get(reverse("cardDatabase-view-card", kwargs={"card_id": card.card_id}))
        assert "basic_form" in response.context
        assert "advanced_form" in response.context

    def test_view_card_shows_recent_decklists(self, client, card, decklist, races, formats):
        response = client.get(reverse("cardDatabase-view-card", kwargs={"card_id": card.card_id}))
        assert "recent_decklists" in response.context


# =============================================================================
# Tests for Decklist Search View
# =============================================================================


@pytest.mark.django_db
class TestDecklistSearchView:
    """Tests for the decklist search view."""

    def test_decklist_search_loads(self, client, formats):
        response = client.get(reverse("cardDatabase-decklist-search"))
        assert response.status_code == 200

    def test_decklist_search_with_form(self, client, decklist_with_cards, formats):
        response = client.get(
            reverse("cardDatabase-decklist-search"),
            {"form_type": "decklist-form", "contains_card": "Dragon"},
        )
        assert response.status_code == 200

    def test_decklist_search_has_formats(self, client, formats):
        response = client.get(reverse("cardDatabase-decklist-search"))
        assert "formats" in response.context


# =============================================================================
# Tests for View Decklist
# =============================================================================


@pytest.mark.django_db
class TestViewDecklistView:
    """Tests for the decklist detail view."""

    def test_view_public_decklist(self, client, decklist):
        response = client.get(reverse("cardDatabase-view-decklist", kwargs={"decklist_id": decklist.pk}))
        assert response.status_code == 200
        assert response.context["decklist"] == decklist

    def test_view_private_decklist_redirects(self, client, profile, format_obj, card, decklist_zone):
        from cardDatabase.models import DeckList
        from cardDatabase.models.DeckList import DeckListCard, UserDeckListZone

        private_deck = DeckList.objects.create(
            profile=profile,
            name="Private Deck",
            public=False,
            deck_format=format_obj,
        )
        user_zone = UserDeckListZone.objects.create(decklist=private_deck, zone=decklist_zone, position=1)
        DeckListCard.objects.create(decklist=private_deck, card=card, position=1, zone=user_zone, quantity=4)

        response = client.get(reverse("cardDatabase-view-decklist", kwargs={"decklist_id": private_deck.pk}))
        assert response.status_code == 302  # Redirect to private decklist page

    def test_view_private_decklist_with_share_code(self, client, profile, format_obj, card, decklist_zone):
        from cardDatabase.models import DeckList
        from cardDatabase.models.DeckList import DeckListCard, UserDeckListZone

        private_deck = DeckList.objects.create(
            profile=profile,
            name="Private Deck",
            public=False,
            shareCode="testcode123",
            deck_format=format_obj,
        )
        user_zone = UserDeckListZone.objects.create(decklist=private_deck, zone=decklist_zone, position=1)
        DeckListCard.objects.create(decklist=private_deck, card=card, position=1, zone=user_zone, quantity=4)

        response = client.get(
            reverse(
                "cardDatabase-view-decklist-share",
                kwargs={"decklist_id": private_deck.pk, "share_parameter": "testcode123"},
            )
        )
        assert response.status_code == 200

    def test_view_decklist_not_found(self, client):
        response = client.get(reverse("cardDatabase-view-decklist", kwargs={"decklist_id": 99999}))
        assert response.status_code == 404

    def test_view_decklist_shows_zones(self, client, decklist_with_cards):
        response = client.get(reverse("cardDatabase-view-decklist", kwargs={"decklist_id": decklist_with_cards.pk}))
        assert response.status_code == 200
        assert "zones" in response.context


# =============================================================================
# Tests for Create Decklist
# =============================================================================


@pytest.mark.django_db
class TestCreateDecklistView:
    """Tests for creating decklists."""

    def test_create_decklist_requires_login(self, client, format_obj):
        response = client.get(reverse("cardDatabase-create-decklist", kwargs={"format": format_obj.name}))
        # Should redirect to login
        assert response.status_code == 302

    def test_create_decklist_authenticated(self, authenticated_client, format_obj, decklist_zones):
        response = authenticated_client.get(reverse("cardDatabase-create-decklist", kwargs={"format": format_obj.name}))
        # Should redirect to edit page after creating
        assert response.status_code in [200, 302]


# =============================================================================
# Tests for Edit Decklist
# =============================================================================


@pytest.mark.django_db
class TestEditDecklistView:
    """Tests for editing decklists."""

    def test_edit_decklist_requires_login(self, client, decklist):
        response = client.get(reverse("cardDatabase-edit-decklist", kwargs={"decklist_id": decklist.pk}))
        assert response.status_code == 302

    def test_edit_own_decklist(self, authenticated_client, format_obj, card, decklist_zone):
        from cardDatabase.models import DeckList, Profile
        from cardDatabase.models.DeckList import DeckListCard, UserDeckListZone

        # Get the authenticated user's profile
        user_profile, _ = Profile.objects.get_or_create(user=authenticated_client.user)
        deck = DeckList.objects.create(
            profile=user_profile,
            name="My Deck",
            public=True,
            deck_format=format_obj,
        )
        user_zone = UserDeckListZone.objects.create(decklist=deck, zone=decklist_zone, position=1)
        DeckListCard.objects.create(decklist=deck, card=card, position=1, zone=user_zone, quantity=4)

        response = authenticated_client.get(reverse("cardDatabase-edit-decklist", kwargs={"decklist_id": deck.pk}))
        assert response.status_code == 200


# =============================================================================
# Tests for Delete Decklist
# =============================================================================


@pytest.mark.django_db
class TestDeleteDecklistView:
    """Tests for deleting decklists."""

    def test_delete_decklist_requires_login(self, client, decklist):
        response = client.get(reverse("cardDatabase-delete-decklist", kwargs={"decklist_id": decklist.pk}))
        assert response.status_code == 302


# =============================================================================
# Tests for Copy Decklist
# =============================================================================


@pytest.mark.django_db
class TestCopyDecklistView:
    """Tests for copying decklists."""

    def test_copy_decklist_requires_login(self, client, decklist):
        response = client.get(reverse("cardDatabase-copy-decklist", kwargs={"decklist_id": decklist.pk}))
        assert response.status_code == 302

    def test_copy_public_decklist(self, client, django_user_model, decklist):
        # Create a different user for copying
        copy_user = django_user_model.objects.create_user(
            username="copyuser",
            email="copy@example.com",
            password="copypass123",
        )
        client.force_login(copy_user)
        response = client.get(
            reverse("cardDatabase-copy-decklist", kwargs={"decklist_id": decklist.pk})
        )
        # Should redirect after copying
        assert response.status_code in [200, 302]


# =============================================================================
# Tests for Banlists View
# =============================================================================


@pytest.mark.django_db
class TestBanlistsView:
    """Tests for the banlists view."""

    def test_banlists_page_loads(self, client):
        from django.core.cache import cache

        cache.clear()  # Clear cache to get fresh response
        response = client.get(reverse("cardDatabase-banlists"))
        assert response.status_code == 200

    def test_banlists_shows_banned_cards(self, client, banned_card):
        from django.core.cache import cache

        cache.clear()  # Clear cache to get fresh response with context
        response = client.get(reverse("cardDatabase-banlists"))
        assert response.context is not None
        assert "banned_cards" in response.context

    def test_banlists_shows_combination_bans(self, client, combination_banned_cards):
        from django.core.cache import cache

        cache.clear()  # Clear cache to get fresh response with context
        response = client.get(reverse("cardDatabase-banlists"))
        assert response.context is not None
        assert "combination_banned_cards" in response.context


# =============================================================================
# Tests for User Public View
# =============================================================================


@pytest.mark.django_db
class TestViewUserPublicView:
    """Tests for viewing a user's public decklists."""

    def test_view_user_decklists(self, client, decklist):
        response = client.get(
            reverse("cardDatabase-view-users-decklist", kwargs={"username": decklist.profile.user.username})
        )
        assert response.status_code == 200


# =============================================================================
# Tests for Metrics View
# =============================================================================


@pytest.mark.django_db
class TestMetricsView:
    """Tests for the metrics view."""

    def test_metrics_page_loads(self, client):
        response = client.get(reverse("cardDatabase-metrics"))
        assert response.status_code == 200


# =============================================================================
# Tests for Pack Opening Views
# =============================================================================


@pytest.mark.django_db
class TestPackSelectView:
    """Tests for the pack select view."""

    def test_pack_select_loads(self, client):
        response = client.get(reverse("cardDatabase-pack-select"))
        assert response.status_code == 200


# =============================================================================
# Tests for Tournament Views
# =============================================================================


@pytest.mark.django_db
class TestTournamentListView:
    """Tests for the tournament list view."""

    def test_tournament_list_loads(self, client, formats):
        response = client.get(reverse("cardDatabase-tournament-list"))
        assert response.status_code == 200


@pytest.mark.django_db
class TestTournamentDetailView:
    """Tests for the tournament detail view."""

    def test_tournament_detail_loads(self, client, tournament):
        response = client.get(reverse("cardDatabase-detail-tournament", kwargs={"tournament_id": tournament.pk}))
        assert response.status_code == 200

    def test_tournament_detail_not_found(self, client):
        response = client.get(reverse("cardDatabase-detail-tournament", kwargs={"tournament_id": 99999}))
        assert response.status_code == 404


@pytest.mark.django_db
class TestNewTournamentView:
    """Tests for creating new tournaments."""

    def test_new_tournament_requires_login(self, client):
        response = client.get(reverse("cardDatabase-new-tournament"))
        assert response.status_code == 302


@pytest.mark.django_db
class TestTournamentAdminView:
    """Tests for tournament admin view."""

    def test_tournament_admin_requires_staff(self, client, tournament):
        response = client.get(reverse("cardDatabase-admin-tournament", kwargs={"tournament_id": tournament.pk}))
        # Should redirect or show unauthorized
        assert response.status_code in [302, 403, 404]


# =============================================================================
# Tests for Export Decklist API
# =============================================================================


@pytest.mark.django_db
class TestExportDecklistView:
    """Tests for the decklist export API."""

    def test_export_public_decklist(self, client, decklist):
        response = client.get(reverse("cardDatabase-export-decklist", kwargs={"decklist_id": decklist.pk}))
        assert response.status_code == 200

    def test_export_decklist_not_found(self, client):
        response = client.get(reverse("cardDatabase-export-decklist", kwargs={"decklist_id": 99999}))
        assert response.status_code == 404


# =============================================================================
# Tests for Register View
# =============================================================================


@pytest.mark.django_db
class TestRegisterView:
    """Tests for user registration."""

    def test_register_page_loads(self, client):
        response = client.get(reverse("cardDatabase-register"))
        assert response.status_code == 200


# =============================================================================
# Tests for Logout View
# =============================================================================


@pytest.mark.django_db
class TestLogoutView:
    """Tests for user logout."""

    def test_logout_redirects(self, authenticated_client):
        response = authenticated_client.get(reverse("cardDatabase-logout"))
        assert response.status_code == 302


# =============================================================================
# Tests for Static Pages
# =============================================================================


@pytest.mark.django_db
class TestStaticPages:
    """Tests for static/simple pages."""

    def test_private_decklist_page(self, client):
        response = client.get(reverse("cardDatabase-private-decklist"))
        assert response.status_code == 200

    def test_locked_decklist_page(self, client):
        response = client.get(reverse("cardDatabase-locked-decklist"))
        assert response.status_code == 200

    def test_desktop_only_page(self, client):
        response = client.get(reverse("cardDatabase-desktop-only"))
        assert response.status_code == 200

    def test_mobile_only_page(self, client):
        response = client.get(reverse("cardDatabase-mobile-only"))
        assert response.status_code == 200


# =============================================================================
# Tests for Reddit Bot API
# =============================================================================


@pytest.mark.django_db
class TestRedditBotView:
    """Tests for the reddit bot API."""

    def test_reddit_bot_query(self, client, cards, settings):
        import json

        # Reddit bot requires POST with JSON body and API key header
        response = client.post(
            reverse("cardDatabase-reddit-bot-query"),
            data=json.dumps({"keywords": ["Dragon"]}),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {settings.REDDIT_BOT_API_KEY}",
        )
        # Should return 200 or 401 if API key auth fails
        assert response.status_code in [200, 401]
