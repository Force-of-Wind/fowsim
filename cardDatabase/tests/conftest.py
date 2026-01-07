"""
Shared pytest fixtures for cardDatabase tests.
"""

import pytest
from django.test import Client
from django.utils import timezone
from datetime import timedelta


@pytest.fixture
def client():
    """Django test client."""
    return Client()


@pytest.fixture
def authenticated_client(client, django_user_model):
    """Django test client with logged-in user."""
    user = django_user_model.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )
    client.force_login(user)
    client.user = user
    return client


@pytest.fixture
def admin_client(client, django_user_model):
    """Django test client with admin user."""
    user = django_user_model.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="adminpass123",
    )
    client.force_login(user)
    client.user = user
    return client


@pytest.fixture
def user(django_user_model):
    """Create a basic test user."""
    return django_user_model.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123",
    )


@pytest.fixture
def profile(user):
    """Get or create a profile for the test user."""
    from cardDatabase.models import Profile

    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


@pytest.fixture
def card_colour():
    """Create a card colour."""
    from cardDatabase.models.CardType import CardColour

    colour, _ = CardColour.objects.get_or_create(name="Fire", db_representation="R")
    return colour


@pytest.fixture
def card_colours():
    """Create all standard card colours."""
    from cardDatabase.models.CardType import CardColour

    colours = [
        ("Fire", "R"),
        ("Water", "U"),
        ("Wind", "G"),
        ("Light", "W"),
        ("Darkness", "B"),
        ("Void", "V"),
    ]
    created = []
    for name, code in colours:
        colour, _ = CardColour.objects.get_or_create(name=name, db_representation=code)
        created.append(colour)
    return created


@pytest.fixture
def card_type():
    """Create a card type."""
    from cardDatabase.models.CardType import Type

    card_type, _ = Type.objects.get_or_create(name="Resonator")
    return card_type


@pytest.fixture
def card_types():
    """Create common card types."""
    from cardDatabase.models.CardType import Type
    from fowsim import constants as CONS

    types = []
    for type_name in ["Resonator", "Chant", "Addition", "Regalia", "Ruler", "J-Ruler", "Magic Stone"]:
        t, _ = Type.objects.get_or_create(name=type_name)
        types.append(t)
    return types


@pytest.fixture
def race():
    """Create a race."""
    from cardDatabase.models.CardType import Race

    race, _ = Race.objects.get_or_create(name="Human")
    return race


@pytest.fixture
def races():
    """Create multiple races."""
    from cardDatabase.models.CardType import Race

    race_names = ["Human", "Dragon", "Fairy", "Beast", "Vampire", ""]
    created = []
    for name in race_names:
        r, _ = Race.objects.get_or_create(name=name)
        created.append(r)
    return created


@pytest.fixture
def format_obj():
    """Create a game format."""
    from cardDatabase.models import Format

    format_obj, _ = Format.objects.get_or_create(name="Wanderer")
    return format_obj


@pytest.fixture
def formats():
    """Create multiple formats."""
    from cardDatabase.models import Format

    format_names = ["Wanderer", "New Frontiers", "Origin", "Paradox"]
    created = []
    for name in format_names:
        f, _ = Format.objects.get_or_create(name=name)
        created.append(f)
    return created


@pytest.fixture
def card(card_colour, card_type, race):
    """Create a basic card."""
    from cardDatabase.models.CardType import Card

    card = Card.objects.create(
        name="Test Card",
        name_without_punctuation="Test Card",
        card_id="TST-001",
        cost="{2}{R}",
        rarity="R",
        ATK=500,
        DEF=500,
    )
    card.colours.add(card_colour)
    card.types.add(card_type)
    card.races.add(race)
    return card


@pytest.fixture
def cards(card_colours, card_types, races):
    """Create multiple cards for testing."""
    from cardDatabase.models.CardType import Card, AbilityText

    cards_data = [
        {"name": "Fire Dragon", "card_id": "TST-001", "cost": "{3}{R}", "rarity": "SR", "ATK": 800, "DEF": 800},
        {"name": "Water Spirit", "card_id": "TST-002", "cost": "{2}{U}", "rarity": "R", "ATK": 400, "DEF": 600},
        {"name": "Wind Fairy", "card_id": "TST-003", "cost": "{1}{G}", "rarity": "C", "ATK": 300, "DEF": 300},
        {"name": "Light Knight", "card_id": "TST-004", "cost": "{2}{W}{W}", "rarity": "U", "ATK": 600, "DEF": 700},
        {"name": "Dark Vampire", "card_id": "TST-005", "cost": "{4}{B}", "rarity": "MR", "ATK": 900, "DEF": 500},
        {"name": "Void Entity", "card_id": "TST-006", "cost": "{5}", "rarity": "SEC", "ATK": 1000, "DEF": 1000},
        {"name": "Multi-Colour Hero", "card_id": "TST-007", "cost": "{1}{R}{U}", "rarity": "R", "ATK": 500, "DEF": 500},
        {"name": "Test Ruler", "card_id": "TST-100", "cost": "", "rarity": "RR", "ATK": None, "DEF": None},
        {"name": "Test J-Ruler", "card_id": "TST-100J", "cost": "", "rarity": "JR", "ATK": 1200, "DEF": 1200},
        {"name": "Basic Stone", "card_id": "TST-101", "cost": "", "rarity": "C", "ATK": None, "DEF": None},
    ]

    created_cards = []
    colour_map = {c.db_representation: c for c in card_colours}
    type_map = {t.name: t for t in card_types}
    race_map = {r.name: r for r in races}

    for i, data in enumerate(cards_data):
        card = Card.objects.create(
            name=data["name"],
            name_without_punctuation=data["name"].lower().replace("-", " "),
            card_id=data["card_id"],
            cost=data["cost"],
            rarity=data["rarity"],
            ATK=data["ATK"],
            DEF=data["DEF"],
        )

        # Assign colours based on cost
        if "{R}" in data["cost"]:
            card.colours.add(colour_map["R"])
        if "{U}" in data["cost"]:
            card.colours.add(colour_map["U"])
        if "{G}" in data["cost"]:
            card.colours.add(colour_map["G"])
        if "{W}" in data["cost"]:
            card.colours.add(colour_map["W"])
        if "{B}" in data["cost"]:
            card.colours.add(colour_map["B"])
        if not card.colours.exists():
            card.colours.add(colour_map["V"])

        # Assign types
        if "Ruler" in data["name"]:
            if "J-" in data["name"]:
                card.types.add(type_map["J-Ruler"])
            else:
                card.types.add(type_map["Ruler"])
        elif "Stone" in data["name"]:
            card.types.add(type_map["Magic Stone"])
        else:
            card.types.add(type_map["Resonator"])

        # Assign races
        if "Dragon" in data["name"]:
            card.races.add(race_map["Dragon"])
        elif "Fairy" in data["name"]:
            card.races.add(race_map["Fairy"])
        elif "Vampire" in data["name"]:
            card.races.add(race_map["Vampire"])
        elif "Knight" in data["name"] or "Hero" in data["name"]:
            card.races.add(race_map["Human"])

        # Add ability text for some cards
        if i < 5:
            ability = AbilityText.objects.create(text=f"Test ability for {data['name']}")
            card.ability_texts.add(ability)

        created_cards.append(card)

    return created_cards


@pytest.fixture
def decklist_zone(format_obj):
    """Create a decklist zone."""
    from cardDatabase.models.DeckList import DeckListZone

    zone, _ = DeckListZone.objects.get_or_create(
        name="Main Deck",
        defaults={"show_by_default": True, "position": 1},
    )
    zone.formats.add(format_obj)
    return zone


@pytest.fixture
def decklist_zones(formats):
    """Create all standard decklist zones."""
    from cardDatabase.models.DeckList import DeckListZone

    zones_data = [
        ("Ruler Area", True, 0),
        ("Main Deck", True, 1),
        ("Magic Stone Deck", True, 2),
        ("Side Deck", True, 3),
    ]
    zones = []
    for name, show, position in zones_data:
        zone, _ = DeckListZone.objects.get_or_create(
            name=name,
            defaults={"show_by_default": show, "position": position},
        )
        for f in formats:
            zone.formats.add(f)
        zones.append(zone)
    return zones


@pytest.fixture
def decklist(profile, format_obj, card, decklist_zone):
    """Create a decklist with cards."""
    from cardDatabase.models import DeckList
    from cardDatabase.models.DeckList import DeckListCard, UserDeckListZone

    decklist = DeckList.objects.create(
        profile=profile,
        name="Test Deck",
        public=True,
        deck_format=format_obj,
    )

    user_zone = UserDeckListZone.objects.create(
        decklist=decklist,
        zone=decklist_zone,
        position=1,
    )

    DeckListCard.objects.create(
        decklist=decklist,
        card=card,
        position=1,
        zone=user_zone,
        quantity=4,
    )

    return decklist


@pytest.fixture
def decklist_with_cards(profile, format_obj, cards, decklist_zones):
    """Create a decklist with multiple cards."""
    from cardDatabase.models import DeckList
    from cardDatabase.models.DeckList import DeckListCard, UserDeckListZone

    decklist = DeckList.objects.create(
        profile=profile,
        name="Full Test Deck",
        public=True,
        deck_format=format_obj,
        comments="A test deck with multiple cards",
    )

    # Create user zones
    user_zones = {}
    for i, zone in enumerate(decklist_zones):
        user_zone = UserDeckListZone.objects.create(
            decklist=decklist,
            zone=zone,
            position=i,
        )
        user_zones[zone.name] = user_zone

    # Add cards to appropriate zones
    position = 1
    for card in cards:
        if "Ruler" in card.name:
            zone = user_zones["Ruler Area"]
            qty = 1
        elif "Stone" in card.name:
            zone = user_zones["Magic Stone Deck"]
            qty = 4
        else:
            zone = user_zones["Main Deck"]
            qty = 4

        DeckListCard.objects.create(
            decklist=decklist,
            card=card,
            position=position,
            zone=zone,
            quantity=qty,
        )
        position += 1

    return decklist


@pytest.fixture
def tournament_level():
    """Create a tournament level."""
    from cardDatabase.models import TournamentLevel

    level, _ = TournamentLevel.objects.get_or_create(
        title="Local",
        defaults={"code": "LC", "hint": "Local store tournament"},
    )
    return level


@pytest.fixture
def tournament(format_obj, tournament_level):
    """Create a tournament."""
    from cardDatabase.models import Tournament

    now = timezone.now()
    tournament = Tournament.objects.create(
        title="Test Tournament",
        meta_data={"description": "A test tournament"},
        is_online=False,
        registration_deadline=now + timedelta(days=7),
        deck_edit_deadline=now + timedelta(days=6),
        start_datetime=now + timedelta(days=8),
        format=format_obj,
        level=tournament_level,
    )
    return tournament


@pytest.fixture
def staff_role():
    """Create a staff role."""
    from cardDatabase.models import StaffRole

    role, _ = StaffRole.objects.get_or_create(
        title="Admin",
        defaults={"can_read": True, "can_write": True, "can_delete": True, "default": False},
    )
    return role


@pytest.fixture
def tournament_staff(tournament, profile, staff_role):
    """Create tournament staff."""
    from cardDatabase.models import TournamentStaff

    staff = TournamentStaff.objects.create(
        profile=profile,
        tournament=tournament,
        role=staff_role,
    )
    return staff


@pytest.fixture
def tournament_player(tournament, profile, decklist):
    """Create a tournament player."""
    from cardDatabase.models import TournamentPlayer
    from fowsim import constants as CONS

    player = TournamentPlayer.objects.create(
        profile=profile,
        tournament=tournament,
        registration_status=CONS.PLAYER_REGISTRATION_ACCEPTED,
        user_data={"name": "Test Player"},
        deck=decklist,
        standing=1,
    )
    return player


@pytest.fixture
def banned_card(card, format_obj):
    """Create a banned card entry."""
    from cardDatabase.models import BannedCard

    banned = BannedCard.objects.create(
        card=card,
        format=format_obj,
    )
    return banned


@pytest.fixture
def combination_banned_cards(cards, format_obj):
    """Create combination banned cards."""
    from cardDatabase.models import CombinationBannedCards

    combo_ban = CombinationBannedCards.objects.create(format=format_obj)
    combo_ban.cards.add(cards[0], cards[1])
    return combo_ban


@pytest.fixture
def pick_period():
    """Create a pick period for metrics."""
    from cardDatabase.models import PickPeriod

    period, _ = PickPeriod.objects.get_or_create(
        days=90,
        defaults={"all_time": False},
    )
    return period


# Query counting context manager for N+1 detection
class QueryCounter:
    """Context manager for counting database queries."""

    def __init__(self, connection=None):
        from django.db import connection as default_connection

        self.connection = connection or default_connection
        self.queries = []

    def __enter__(self):
        self.queries = []
        self._initial_queries = len(self.connection.queries)
        return self

    def __exit__(self, *args):
        self.queries = self.connection.queries[self._initial_queries :]

    @property
    def count(self):
        return len(self.queries)

    def assert_max_queries(self, max_queries, msg=None):
        """Assert that at most max_queries were executed."""
        if self.count > max_queries:
            query_log = "\n".join(f"  {i+1}. {q['sql'][:100]}..." for i, q in enumerate(self.queries))
            default_msg = f"Expected at most {max_queries} queries, but {self.count} were executed:\n{query_log}"
            raise AssertionError(msg or default_msg)


@pytest.fixture
def query_counter():
    """Fixture for counting queries."""
    return QueryCounter


@pytest.fixture
def assert_max_queries(settings):
    """Fixture for asserting maximum query count."""
    settings.DEBUG = True  # Required for query logging

    def _assert_max_queries(max_queries):
        return QueryCounter()

    return _assert_max_queries
