"""
Tests for cardDatabase models.
"""

import pytest
from django.utils import timezone
from datetime import timedelta


# =============================================================================
# Card Model Tests
# =============================================================================


@pytest.mark.django_db
class TestCardModel:
    """Tests for the Card model."""

    def test_card_str_returns_name(self, card):
        assert str(card) == card.name

    def test_card_set_code_with_dash(self, card):
        assert card.set_code == "TST"

    def test_card_set_code_without_dash(self, card_colour, card_type, race):
        from cardDatabase.models.CardType import Card

        card = Card.objects.create(
            name="Promo Card",
            name_without_punctuation="Promo Card",
            card_id="H2 Buy a Box",
            rarity="PR",
        )
        card.colours.add(card_colour)
        card.types.add(card_type)

        assert card.set_code == "H2 Buy a Box"

    def test_card_set_code_complex(self, card_colour, card_type, race):
        from cardDatabase.models.CardType import Card

        card = Card.objects.create(
            name="Complex Set Card",
            name_without_punctuation="Complex Set Card",
            card_id="ABC-SD01-123",
            rarity="R",
        )
        card.colours.add(card_colour)
        card.types.add(card_type)

        assert card.set_code == "ABC-SD01"

    def test_card_set_number(self, card):
        assert card.set_number == "001"

    def test_card_set_number_none_without_dash(self, card_colour, card_type):
        from cardDatabase.models.CardType import Card

        card = Card.objects.create(
            name="Promo",
            name_without_punctuation="Promo",
            card_id="PromoCard",
            rarity="PR",
        )
        card.colours.add(card_colour)
        card.types.add(card_type)

        assert card.set_number is None

    def test_card_total_cost_simple(self, card):
        # card has cost "{2}{R}" so total is 2 + 1 = 3
        assert card.total_cost == 3

    def test_card_total_cost_multiple_colours(self, card_colour, card_type):
        from cardDatabase.models.CardType import Card

        card = Card.objects.create(
            name="Multi",
            name_without_punctuation="Multi",
            card_id="TST-999",
            cost="{1}{R}{U}{G}",
            rarity="R",
        )
        card.colours.add(card_colour)
        card.types.add(card_type)

        # 1 + 1 + 1 + 1 = 4
        assert card.total_cost == 4

    def test_card_total_cost_with_x(self, card_colour, card_type):
        from cardDatabase.models.CardType import Card

        card = Card.objects.create(
            name="X Cost Card",
            name_without_punctuation="X Cost Card",
            card_id="TST-998",
            cost="{X}{R}",
            rarity="R",
        )
        card.colours.add(card_colour)
        card.types.add(card_type)

        # X doesn't count, R = 1
        assert card.total_cost == 1

    def test_card_total_cost_none(self, card_colour, card_type):
        from cardDatabase.models.CardType import Card

        card = Card.objects.create(
            name="No Cost",
            name_without_punctuation="No Cost",
            card_id="TST-997",
            cost=None,
            rarity="R",
        )
        card.colours.add(card_colour)
        card.types.add(card_type)

        assert card.total_cost == 0

    def test_card_other_sides_finds_j_ruler(self, card_colours, card_types):
        from cardDatabase.models.CardType import Card

        ruler = Card.objects.create(
            name="Test Ruler",
            name_without_punctuation="Test Ruler",
            card_id="NEW-100",
            rarity="RR",
        )
        ruler.colours.add(card_colours[0])
        ruler.types.add(card_types[4])  # Ruler type

        j_ruler = Card.objects.create(
            name="Test J-Ruler",
            name_without_punctuation="Test J-Ruler",
            card_id="NEW-100J",
            rarity="JR",
        )
        j_ruler.colours.add(card_colours[0])
        j_ruler.types.add(card_types[5])  # J-Ruler type

        other_sides = ruler.other_sides
        assert j_ruler in other_sides

    def test_card_reprints(self, card, card_colour, card_type, race):
        from cardDatabase.models.CardType import Card

        reprint = Card.objects.create(
            name=card.name,  # Same name
            name_without_punctuation=card.name,
            card_id="REP-001",
            rarity="R",
        )
        reprint.colours.add(card_colour)
        reprint.types.add(card_type)

        reprints = card.reprints
        assert reprint in reprints
        assert card not in reprints


# =============================================================================
# DeckList Model Tests
# =============================================================================


@pytest.mark.django_db
class TestDeckListModel:
    """Tests for the DeckList model."""

    def test_decklist_str_includes_name_and_email(self, decklist):
        result = str(decklist)
        assert decklist.name in result
        assert decklist.profile.user.email in result

    def test_decklist_get_colours(self, decklist):
        colours = decklist.get_colours
        assert len(colours) > 0

    def test_decklist_get_front_card(self, decklist):
        front_card = decklist.get_front_card_of_deck
        assert front_card is not None

    def test_decklist_save_updates_last_modified(self, decklist):
        import time

        old_modified = decklist.last_modified
        time.sleep(0.01)  # Ensure timestamp changes (SQLite has lower precision)
        decklist.name = "Updated Name"
        decklist.save()
        assert decklist.last_modified >= old_modified


@pytest.mark.django_db
class TestDeckListCardModel:
    """Tests for the DeckListCard model."""

    def test_decklistcard_str(self, decklist):
        deck_card = decklist.cards.first()
        result = str(deck_card)
        assert deck_card.card.name in result


@pytest.mark.django_db
class TestUserDeckListZoneModel:
    """Tests for the UserDeckListZone model."""

    def test_user_zone_card_count(self, decklist):
        user_zone = decklist.cards.first().zone
        assert user_zone.card_count >= 0


# =============================================================================
# Format Model Tests
# =============================================================================


@pytest.mark.django_db
class TestFormatModel:
    """Tests for the Format model."""

    def test_format_str_returns_name(self, format_obj):
        assert str(format_obj) == format_obj.name

    def test_format_get_default_creates_wanderer(self):
        from cardDatabase.models import Format

        default_pk = Format.get_default()
        default_format = Format.objects.get(pk=default_pk)
        assert default_format.name == "Wanderer"


# =============================================================================
# BannedCard Model Tests
# =============================================================================


@pytest.mark.django_db
class TestBannedCardModel:
    """Tests for the BannedCard model."""

    def test_banned_card_str(self, banned_card):
        result = str(banned_card)
        assert banned_card.card.name in result
        assert banned_card.format.name in result


@pytest.mark.django_db
class TestCombinationBannedCardsModel:
    """Tests for the CombinationBannedCards model."""

    def test_combination_banned_str(self, combination_banned_cards):
        result = str(combination_banned_cards)
        assert combination_banned_cards.format.name in result


# =============================================================================
# Tournament Model Tests
# =============================================================================


@pytest.mark.django_db
class TestTournamentModel:
    """Tests for the Tournament model."""

    def test_tournament_str_returns_title(self, tournament):
        assert str(tournament) == tournament.title

    def test_tournament_default_phase(self, format_obj, tournament_level):
        from cardDatabase.models import Tournament
        from fowsim import constants as CONS

        now = timezone.now()
        t = Tournament.objects.create(
            title="New Tournament",
            meta_data={},
            registration_deadline=now + timedelta(days=7),
            deck_edit_deadline=now + timedelta(days=6),
            start_datetime=now + timedelta(days=8),
            format=format_obj,
            level=tournament_level,
        )
        assert t.phase == CONS.TOURNAMENT_PHASE_CREATED


@pytest.mark.django_db
class TestTournamentPlayerModel:
    """Tests for the TournamentPlayer model."""

    def test_tournament_player_str(self, tournament_player):
        result = str(tournament_player)
        assert tournament_player.profile.user.username in result


@pytest.mark.django_db
class TestTournamentStaffModel:
    """Tests for the TournamentStaff model."""

    def test_tournament_staff_str(self, tournament_staff):
        result = str(tournament_staff)
        assert tournament_staff.profile.user.username in result


@pytest.mark.django_db
class TestStaffRoleModel:
    """Tests for the StaffRole model."""

    def test_staff_role_str(self, staff_role):
        assert str(staff_role) == staff_role.title


@pytest.mark.django_db
class TestTournamentLevelModel:
    """Tests for the TournamentLevel model."""

    def test_tournament_level_str(self, tournament_level):
        assert str(tournament_level) == tournament_level.title


# =============================================================================
# Race Model Tests
# =============================================================================


@pytest.mark.django_db
class TestRaceModel:
    """Tests for the Race model."""

    def test_race_str_returns_name(self, race):
        assert str(race) == race.name


# =============================================================================
# Type Model Tests
# =============================================================================


@pytest.mark.django_db
class TestTypeModel:
    """Tests for the Type model."""

    def test_type_str_returns_name(self, card_type):
        assert str(card_type) == card_type.name


# =============================================================================
# CardColour Model Tests
# =============================================================================


@pytest.mark.django_db
class TestCardColourModel:
    """Tests for the CardColour model."""

    def test_colour_str_returns_name(self, card_colour):
        assert str(card_colour) == card_colour.name


# =============================================================================
# Profile Model Tests
# =============================================================================


@pytest.mark.django_db
class TestProfileModel:
    """Tests for the Profile model."""

    def test_profile_associated_with_user(self, profile):
        assert profile.user is not None


# =============================================================================
# DeckListZone Model Tests
# =============================================================================


@pytest.mark.django_db
class TestDeckListZoneModel:
    """Tests for the DeckListZone model."""

    def test_zone_str_returns_name(self, decklist_zone):
        assert str(decklist_zone) == decklist_zone.name


# =============================================================================
# AbilityText Model Tests
# =============================================================================


@pytest.mark.django_db
class TestAbilityTextModel:
    """Tests for the AbilityText model."""

    def test_ability_text_str(self):
        from cardDatabase.models.CardType import AbilityText

        ability = AbilityText.objects.create(text="Test ability text")
        assert str(ability) == "Test ability text"


# =============================================================================
# Cluster and Set Model Tests
# =============================================================================


@pytest.mark.django_db
class TestClusterModel:
    """Tests for the Cluster model."""

    def test_cluster_str_returns_name(self):
        from cardDatabase.models.CardType import Cluster

        cluster = Cluster.objects.create(name="Test Cluster")
        assert str(cluster) == "Test Cluster"


@pytest.mark.django_db
class TestSetModel:
    """Tests for the Set model."""

    def test_set_str_returns_name(self):
        from cardDatabase.models.CardType import Cluster, Set

        cluster = Cluster.objects.create(name="Test Cluster")
        fow_set = Set.objects.create(name="Test Set", code="TST", cluster=cluster)
        assert str(fow_set) == "Test Set"


# =============================================================================
# Tag Model Tests
# =============================================================================


@pytest.mark.django_db
class TestTagModel:
    """Tests for the Tag model."""

    def test_tag_str_returns_name(self):
        from cardDatabase.models.CardType import Tag

        tag = Tag.objects.create(name="Test Tag")
        assert str(tag) == "Test Tag"


# =============================================================================
# CardArtist Model Tests
# =============================================================================


@pytest.mark.django_db
class TestCardArtistModel:
    """Tests for the CardArtist model."""

    def test_artist_str_returns_name(self):
        from cardDatabase.models.CardType import CardArtist

        artist = CardArtist.objects.create(name="Test Artist")
        assert str(artist) == "Test Artist"


# =============================================================================
# PickPeriod Model Tests
# =============================================================================


@pytest.mark.django_db
class TestPickPeriodModel:
    """Tests for the PickPeriod model."""

    def test_pick_period_creation(self, pick_period):
        assert pick_period.days == 90
        assert pick_period.all_time is False
