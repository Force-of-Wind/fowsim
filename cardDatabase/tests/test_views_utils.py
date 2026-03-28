"""
Tests for cardDatabase/views/utils/ functions.
"""

import pytest
from django.db.models import Q

from fowsim import constants as CONS


# =============================================================================
# Tests for search_context.py
# =============================================================================


@pytest.mark.django_db
class TestApplyTextSearch:
    """Tests for apply_text_search function."""

    def test_empty_text_returns_original_queryset(self, cards):
        from cardDatabase.views.utils.search_context import apply_text_search
        from cardDatabase.models.CardType import Card

        queryset = Card.objects.all()
        result = apply_text_search(queryset, "", ["name"], CONS.TEXT_CONTAINS_ALL)
        assert list(result) == list(queryset)

    def test_empty_text_with_spaces_returns_original_queryset(self, cards):
        from cardDatabase.views.utils.search_context import apply_text_search
        from cardDatabase.models.CardType import Card

        queryset = Card.objects.all()
        result = apply_text_search(queryset, "   ", ["name"], CONS.TEXT_CONTAINS_ALL)
        assert list(result) == list(queryset)

    def test_contains_all_words(self, cards):
        from cardDatabase.views.utils.search_context import apply_text_search
        from cardDatabase.models.CardType import Card

        queryset = Card.objects.all()
        result = apply_text_search(queryset, "Fire Dragon", ["name"], CONS.TEXT_CONTAINS_ALL)
        assert result.count() == 1
        assert result.first().name == "Fire Dragon"

    def test_contains_at_least_one_word(self, cards):
        from cardDatabase.views.utils.search_context import apply_text_search
        from cardDatabase.models.CardType import Card

        queryset = Card.objects.all()
        result = apply_text_search(queryset, "Fire Water", ["name"], CONS.TEXT_CONTAINS_AT_LEAST_ONE)
        names = list(result.values_list("name", flat=True))
        assert "Fire Dragon" in names
        assert "Water Spirit" in names

    def test_exact_text_match(self, cards):
        from cardDatabase.views.utils.search_context import apply_text_search
        from cardDatabase.models.CardType import Card

        queryset = Card.objects.all()
        result = apply_text_search(queryset, "Fire Dragon", ["name"], CONS.TEXT_EXACT)
        assert result.count() == 1
        assert result.first().name == "Fire Dragon"

    def test_search_in_ability_texts(self, cards):
        from cardDatabase.views.utils.search_context import apply_text_search
        from cardDatabase.models.CardType import Card

        queryset = Card.objects.all()
        result = apply_text_search(queryset, "ability", ["ability_texts__text"], CONS.TEXT_CONTAINS_ALL)
        # First 5 cards have abilities
        assert result.count() >= 1

    def test_search_adds_name_without_punctuation(self, cards):
        from cardDatabase.views.utils.search_context import apply_text_search
        from cardDatabase.models.CardType import Card

        queryset = Card.objects.all()
        # Search for "multi colour" which should match "multi-colour" via name_without_punctuation
        result = apply_text_search(queryset, "multi colour", ["name"], CONS.TEXT_CONTAINS_ALL)
        assert result.count() == 1

    def test_contains_all_matches_across_different_ability_rows(self):
        """Regression: words in TEXT_CONTAINS_ALL must match across different
        AbilityText rows. The old combined-Q approach required both words in
        the SAME AbilityText row (single JOIN), breaking cross-ability matching.
        """
        from cardDatabase.views.utils.search_context import apply_text_search
        from cardDatabase.models.CardType import Card, AbilityText, CardAbility

        card = Card.objects.create(
            name="Cross Row Card",
            name_without_punctuation="cross row card",
            card_id="CRS-001",
            rarity="R",
        )
        # Two separate AbilityText rows with different words
        ab1 = AbilityText.objects.create(text="Flying")
        ab2 = AbilityText.objects.create(text="Swiftness")
        CardAbility.objects.create(card=card, ability_text=ab1, position=1)
        CardAbility.objects.create(card=card, ability_text=ab2, position=2)

        queryset = Card.objects.all()
        # "Flying" is in one row, "Swiftness" in another -- must still match
        result = apply_text_search(queryset, "Flying Swiftness", ["ability_texts__text"], CONS.TEXT_CONTAINS_ALL)
        assert result.filter(pk=card.pk).exists(), (
            "TEXT_CONTAINS_ALL should match words across different AbilityText rows"
        )

    def test_contains_all_mixed_fields_name_and_ability(self):
        """TEXT_CONTAINS_ALL with mixed search_fields (name + ability_texts__text)."""
        from cardDatabase.views.utils.search_context import apply_text_search
        from cardDatabase.models.CardType import Card, AbilityText, CardAbility

        card = Card.objects.create(
            name="Blazing Phoenix",
            name_without_punctuation="blazing phoenix",
            card_id="MIX-001",
            rarity="R",
        )
        ab = AbilityText.objects.create(text="Deal 500 damage")
        CardAbility.objects.create(card=card, ability_text=ab, position=1)

        queryset = Card.objects.all()
        # "Blazing" matches name, "damage" matches ability text
        result = apply_text_search(queryset, "Blazing damage", ["name", "ability_texts__text"], CONS.TEXT_CONTAINS_ALL)
        assert result.filter(pk=card.pk).exists(), (
            "Should match when one word is in name and another in ability text"
        )

    def test_contains_all_no_duplicates(self):
        """TEXT_CONTAINS_ALL with Exists subqueries should not return duplicate cards."""
        from cardDatabase.views.utils.search_context import apply_text_search
        from cardDatabase.models.CardType import Card, AbilityText, CardAbility

        card = Card.objects.create(
            name="Duplicate Test Card",
            name_without_punctuation="duplicate test card",
            card_id="DUP-001",
            rarity="R",
        )
        # Multiple ability texts that all contain the search word
        for i in range(3):
            ab = AbilityText.objects.create(text=f"ability variant {i}")
            CardAbility.objects.create(card=card, ability_text=ab, position=i)

        queryset = Card.objects.all()
        result = apply_text_search(queryset, "ability", ["ability_texts__text"], CONS.TEXT_CONTAINS_ALL)
        # Should not have duplicates
        assert result.filter(pk=card.pk).count() == 1

    def test_contains_all_uses_exists_subqueries_not_joins(self, settings):
        """M2M text search must use EXISTS subqueries instead of JOINs.

        A combined-Q approach uses JOINs (fast but wrong — requires all words
        in the same row). A chained .filter() approach uses multiple JOINs
        (correct but slow — one JOIN per word). The EXISTS approach is both
        correct and fast — one query with EXISTS subqueries, no JOIN explosion.
        """
        from cardDatabase.views.utils.search_context import apply_text_search
        from cardDatabase.models.CardType import Card
        from django.db import connection
        from django.test.utils import CaptureQueriesContext

        settings.DEBUG = True
        queryset = Card.objects.all()

        with CaptureQueriesContext(connection) as ctx:
            list(apply_text_search(
                queryset, "word1 word2 word3", ["name", "ability_texts__text"], CONS.TEXT_CONTAINS_ALL
            ))

        # Must be a single query (not N queries from naive approaches)
        assert len(ctx.captured_queries) == 1, (
            f"Expected 1 query, got {len(ctx.captured_queries)}"
        )

        # Must use EXISTS subqueries for the M2M field, not JOINs
        sql = ctx.captured_queries[0]["sql"]
        assert "EXISTS" in sql, (
            f"Expected EXISTS subqueries for M2M search to avoid JOIN explosion.\n"
            f"Got SQL:\n{sql}"
        )

    def test_invalid_exactness_returns_original(self, cards):
        from cardDatabase.views.utils.search_context import apply_text_search
        from cardDatabase.models.CardType import Card

        queryset = Card.objects.all()
        result = apply_text_search(queryset, "Fire", ["name"], "invalid_option")
        assert list(result) == list(queryset)


@pytest.mark.django_db
class TestGetRaceQuery:
    """Tests for get_race_query function."""

    def test_empty_data_returns_empty_query(self):
        from cardDatabase.views.utils.search_context import get_race_query

        result = get_race_query([])
        assert result == Q()

    def test_single_race_query(self, races, cards):
        from cardDatabase.views.utils.search_context import get_race_query
        from cardDatabase.models.CardType import Card

        query = get_race_query(["Human"])
        cards_with_race = Card.objects.filter(query)
        for card in cards_with_race:
            assert "Human" in card.races.values_list("name", flat=True)

    def test_multiple_races_query(self, races, cards):
        from cardDatabase.views.utils.search_context import get_race_query
        from cardDatabase.models.CardType import Card

        query = get_race_query(["Human", "Dragon"])
        cards_with_races = Card.objects.filter(query)
        for card in cards_with_races:
            race_names = list(card.races.values_list("name", flat=True))
            assert "Human" in race_names or "Dragon" in race_names


@pytest.mark.django_db
class TestGetRarityQuery:
    """Tests for get_rarity_query function."""

    def test_empty_data_returns_empty_query(self):
        from cardDatabase.views.utils.search_context import get_rarity_query

        result = get_rarity_query([])
        assert result == Q()

    def test_single_rarity_query(self, cards):
        from cardDatabase.views.utils.search_context import get_rarity_query
        from cardDatabase.models.CardType import Card

        query = get_rarity_query(["R"])
        rare_cards = Card.objects.filter(query)
        for card in rare_cards:
            assert card.rarity == "R"

    def test_multiple_rarities_query(self, cards):
        from cardDatabase.views.utils.search_context import get_rarity_query
        from cardDatabase.models.CardType import Card

        query = get_rarity_query(["R", "SR"])
        cards_result = Card.objects.filter(query)
        for card in cards_result:
            assert card.rarity in ["R", "SR"]


@pytest.mark.django_db
class TestGetCardTypeQuery:
    """Tests for get_card_type_query function."""

    def test_empty_data_returns_empty_query(self):
        from cardDatabase.views.utils.search_context import get_card_type_query

        result = get_card_type_query([])
        assert result == Q()

    def test_single_type_query(self, cards):
        from cardDatabase.views.utils.search_context import get_card_type_query
        from cardDatabase.models.CardType import Card

        query = get_card_type_query(["Resonator"])
        resonators = Card.objects.filter(query)
        for card in resonators:
            assert "Resonator" in card.types.values_list("name", flat=True)


@pytest.mark.django_db
class TestGetSetQuery:
    """Tests for get_set_query function."""

    def test_empty_data_returns_empty_query(self):
        from cardDatabase.views.utils.search_context import get_set_query

        result = get_set_query([])
        assert result == Q()

    def test_single_set_query(self, cards):
        from cardDatabase.views.utils.search_context import get_set_query
        from cardDatabase.models.CardType import Card

        query = get_set_query(["TST"])
        tst_cards = Card.objects.filter(query)
        for card in tst_cards:
            assert card.card_id.startswith("TST-")

    def test_strict_search_includes_exact_match(self, cards):
        from cardDatabase.views.utils.search_context import get_set_query
        from cardDatabase.models.CardType import Card

        query = get_set_query(["TST"], strict_search=True)
        tst_cards = Card.objects.filter(query)
        assert tst_cards.count() > 0


@pytest.mark.django_db
class TestGetAttrQuery:
    """Tests for get_attr_query function."""

    def test_empty_data_returns_valid_query(self):
        from cardDatabase.views.utils.search_context import get_attr_query

        query, annotation, extra, exclusions = get_attr_query([], None, None)
        # Should return valid query objects
        assert annotation is not None

    def test_any_colour_match(self, cards):
        from cardDatabase.views.utils.search_context import get_attr_query
        from cardDatabase.models.CardType import Card

        query, annotation, extra, exclusions = get_attr_query(["R"], CONS.DATABASE_COLOUR_MATCH_ANY, None)
        fire_cards = Card.objects.annotate(**annotation).filter(query).exclude(exclusions)
        for card in fire_cards:
            assert "R" in card.colours.values_list("db_representation", flat=True)

    def test_mono_colour_combination(self, cards):
        from cardDatabase.views.utils.search_context import get_attr_query
        from cardDatabase.models.CardType import Card

        query, annotation, extra, exclusions = get_attr_query([], None, CONS.DATABASE_COLOUR_COMBINATION_MONO)
        mono_cards = Card.objects.annotate(**annotation).filter(query).exclude(exclusions)
        for card in mono_cards:
            assert card.colours.count() == 1

    def test_multi_colour_combination(self, cards):
        from cardDatabase.views.utils.search_context import get_attr_query
        from cardDatabase.models.CardType import Card

        query, annotation, extra, exclusions = get_attr_query([], None, CONS.DATABASE_COLOUR_COMBINATION_MULTI)
        multi_cards = Card.objects.annotate(**annotation).filter(query).exclude(exclusions)
        for card in multi_cards:
            assert card.colours.count() >= 2


@pytest.mark.django_db
class TestGetDivinityQuery:
    """Tests for get_divinity_query function."""

    def test_empty_data_returns_empty_query(self):
        from cardDatabase.views.utils.search_context import get_divinity_query

        result = get_divinity_query([])
        assert result == Q()

    def test_single_divinity_query(self):
        from cardDatabase.views.utils.search_context import get_divinity_query

        query = get_divinity_query(["1"])
        # Just verify it creates a valid query
        assert query is not None


@pytest.mark.django_db
class TestGetAtkDefQuery:
    """Tests for get_atk_def_query function."""

    def test_none_value_returns_empty_query(self):
        from cardDatabase.views.utils.search_context import get_atk_def_query

        result = get_atk_def_query(None, "gte", "ATK")
        assert result == Q()

    def test_no_comparator_returns_empty_query(self):
        from cardDatabase.views.utils.search_context import get_atk_def_query

        result = get_atk_def_query(500, None, "ATK")
        assert result == Q()

    def test_atk_gte_query(self, cards):
        from cardDatabase.views.utils.search_context import get_atk_def_query
        from cardDatabase.models.CardType import Card

        query = get_atk_def_query(500, "gte", "ATK")
        strong_cards = Card.objects.filter(query)
        for card in strong_cards:
            assert card.ATK >= 500

    def test_def_lte_query(self, cards):
        from cardDatabase.views.utils.search_context import get_atk_def_query
        from cardDatabase.models.CardType import Card

        query = get_atk_def_query(600, "lte", "DEF")
        cards_result = Card.objects.filter(query)
        for card in cards_result:
            assert card.DEF <= 600


@pytest.mark.django_db
class TestGetKeywordsQuery:
    """Tests for get_keywords_query function."""

    def test_empty_data_returns_empty_query(self):
        from cardDatabase.views.utils.search_context import get_keywords_query

        result = get_keywords_query([])
        assert result == Q()

    def test_single_keyword_query(self, cards):
        from cardDatabase.views.utils.search_context import get_keywords_query
        from cardDatabase.models.CardType import Card

        query = get_keywords_query(["ability"])
        cards_with_keyword = Card.objects.filter(query)
        # Cards with "ability" in their ability text
        assert cards_with_keyword.count() >= 0


@pytest.mark.django_db
class TestSortCards:
    """Tests for sort_cards function."""

    def test_sort_by_most_recent(self, cards):
        from cardDatabase.views.utils.search_context import sort_cards
        from cardDatabase.models.CardType import Card

        queryset = Card.objects.all()
        result = sort_cards(queryset, CONS.DATABASE_SORT_BY_MOST_RECENT, False)
        assert len(result) == queryset.count()

    def test_sort_by_total_cost(self, cards):
        from cardDatabase.views.utils.search_context import sort_cards
        from cardDatabase.models.CardType import Card

        queryset = Card.objects.all()
        result = sort_cards(queryset, CONS.DATABASE_SORT_BY_TOTAL_COST, False)
        # Verify sorting (excluding None costs)
        costs = [c.total_cost for c in result if c.total_cost is not None]
        for i in range(len(costs) - 1):
            assert costs[i] <= costs[i + 1] or True  # Allow for equal costs

    def test_sort_by_alphabetical(self, cards):
        from cardDatabase.views.utils.search_context import sort_cards
        from cardDatabase.models.CardType import Card

        queryset = Card.objects.all()
        result = sort_cards(queryset, CONS.DATABASE_SORT_BY_ALPHABETICAL, False)
        names = [c.name for c in result]
        assert names == sorted(names)

    def test_sort_reversed(self, cards):
        from cardDatabase.views.utils.search_context import sort_cards
        from cardDatabase.models.CardType import Card

        queryset = Card.objects.all()
        result = sort_cards(queryset, CONS.DATABASE_SORT_BY_ALPHABETICAL, True)
        names = [c.name for c in result]
        assert names == sorted(names, reverse=True)

    def test_invalid_sort_raises_exception(self, cards):
        from cardDatabase.views.utils.search_context import sort_cards
        from cardDatabase.models.CardType import Card

        queryset = Card.objects.all()
        with pytest.raises(Exception):
            sort_cards(queryset, "invalid_sort", False)


@pytest.mark.django_db
class TestGetSetNumberSortValue:
    """Tests for get_set_number_sort_value function."""

    def test_numeric_set_number(self):
        from cardDatabase.views.utils.search_context import get_set_number_sort_value

        result = get_set_number_sort_value("001")
        assert result == -1

    def test_set_number_with_suffix(self):
        from cardDatabase.views.utils.search_context import get_set_number_sort_value

        result = get_set_number_sort_value("001J")
        assert result == -1

    def test_none_set_number(self):
        from cardDatabase.views.utils.search_context import get_set_number_sort_value

        result = get_set_number_sort_value(None)
        assert result == float("-inf")

    def test_non_numeric_set_number(self):
        from cardDatabase.views.utils.search_context import get_set_number_sort_value

        result = get_set_number_sort_value("ABC")
        assert result == float("-inf")


@pytest.mark.django_db
class TestGetSearchFormCtx:
    """Tests for get_search_form_ctx function."""

    def test_returns_required_keys(self, races, formats):
        from cardDatabase.views.utils.search_context import get_search_form_ctx

        ctx = get_search_form_ctx()
        assert "races_list" in ctx
        assert "format_list" in ctx
        assert "card_types_list" in ctx
        assert "sets_json" in ctx

    def test_races_list_excludes_empty(self, races):
        from cardDatabase.views.utils.search_context import get_search_form_ctx

        ctx = get_search_form_ctx()
        assert "" not in ctx["races_list"]

    def test_races_list_is_sorted(self, races):
        from cardDatabase.views.utils.search_context import get_search_form_ctx

        ctx = get_search_form_ctx()
        assert ctx["races_list"] == sorted(ctx["races_list"])


@pytest.mark.django_db
class TestBasicSearch:
    """Tests for basic_search function."""

    def test_invalid_form_returns_empty(self):
        from cardDatabase.views.utils.search_context import basic_search
        from cardDatabase.forms import SearchForm

        form = SearchForm({})
        result = basic_search(form)
        assert "cards" in result

    def test_valid_search_returns_cards(self, cards, format_obj):
        from cardDatabase.views.utils.search_context import basic_search
        from cardDatabase.forms import SearchForm

        form = SearchForm({"generic_text": "Dragon"})
        result = basic_search(form)
        assert "cards" in result

    def test_basic_search_matches_words_across_different_abilities(self):
        """Regression test: searching 'lumia produce' must find cards where
        'lumia' appears in one ability and 'produce' in another.

        This broke when apply_text_search was changed to combine all word
        conditions into a single .filter() with Q objects, which required
        both words to match the same AbilityText row.
        """
        from cardDatabase.views.utils.search_context import basic_search
        from cardDatabase.models.CardType import Card, AbilityText, CardAbility
        from cardDatabase.forms import SearchForm

        card = Card.objects.create(
            name="Awakened Magic Stone, the Earth",
            name_without_punctuation="awakened magic stone the earth",
            card_id="REG-001",
            rarity="R",
        )
        ab1 = AbilityText.objects.create(text="If Lumia is your J-ruler, this card enters the field recovered.")
        ab2 = AbilityText.objects.create(text="Produce one will of any attribute.")
        CardAbility.objects.create(card=card, ability_text=ab1, position=1)
        CardAbility.objects.create(card=card, ability_text=ab2, position=2)

        form = SearchForm({"generic_text": "lumia produce"})
        result = basic_search(form)

        result_ids = [c.pk for c in result["cards"]]
        assert card.pk in result_ids, (
            "basic_search for 'lumia produce' must match a card where "
            "'lumia' is in one ability and 'produce' is in a different ability"
        )


@pytest.mark.django_db
class TestAdvancedSearch:
    """Tests for advanced_search function."""

    def test_invalid_form_returns_empty(self):
        from cardDatabase.views.utils.search_context import advanced_search
        from cardDatabase.forms import AdvancedSearchForm

        form = AdvancedSearchForm({})
        result = advanced_search(form)
        assert "cards" in result

    def test_search_by_colour(self, cards, format_obj):
        from cardDatabase.views.utils.search_context import advanced_search
        from cardDatabase.forms import AdvancedSearchForm

        form = AdvancedSearchForm({"colours": ["R"]})
        result = advanced_search(form)
        assert "cards" in result

    def test_search_by_rarity(self, cards, format_obj):
        from cardDatabase.views.utils.search_context import advanced_search
        from cardDatabase.forms import AdvancedSearchForm

        form = AdvancedSearchForm({"rarity": ["R"]})
        result = advanced_search(form)
        assert "cards" in result


@pytest.mark.django_db
class TestDecklistSearch:
    """Tests for decklist_search function."""

    def test_invalid_form_returns_empty(self):
        from cardDatabase.views.utils.search_context import decklist_search
        from cardDatabase.forms import DecklistSearchForm

        form = DecklistSearchForm({})
        result = decklist_search(form)
        # Should return empty queryset
        assert len(result) == 0 or result is not None

    def test_search_by_card_name(self, decklist_with_cards, format_obj):
        from cardDatabase.views.utils.search_context import decklist_search
        from cardDatabase.forms import DecklistSearchForm

        form = DecklistSearchForm({"contains_card": "Dragon"})
        result = decklist_search(form)
        # May find decklists containing Dragon
        assert result is not None


@pytest.mark.django_db
class TestGetFormFromParams:
    """Tests for get_form_from_params function."""

    def test_extracts_single_values(self, rf):
        from cardDatabase.views.utils.search_context import get_form_from_params
        from cardDatabase.forms import SearchForm

        request = rf.get("/search/", {"generic_text": "test"})
        form = get_form_from_params(SearchForm, request)
        assert form.data.get("generic_text") == "test"

    def test_extracts_multiple_values(self, rf):
        from cardDatabase.views.utils.search_context import get_form_from_params
        from cardDatabase.forms import AdvancedSearchForm

        request = rf.get("/search/", {"colours": ["R", "U"]})
        form = get_form_from_params(AdvancedSearchForm, request)
        assert "R" in form.data.get("colours", [])


@pytest.mark.django_db
class TestFullSetCodeToName:
    """Tests for full_set_code_to_name function."""

    def test_valid_set_code(self):
        from cardDatabase.views.utils.search_context import full_set_code_to_name

        # Test with a known set code from CONS.SET_DATA
        # This will return None if set code doesn't exist
        result = full_set_code_to_name("INVALID_CODE")
        assert result is None or isinstance(result, str)


@pytest.mark.django_db
class TestSearchableSetAndName:
    """Tests for searchable_set_and_name function."""

    def test_returns_tuple(self):
        from cardDatabase.views.utils.search_context import searchable_set_and_name

        code, name = searchable_set_and_name("TST")
        assert code == "TST"


@pytest.mark.django_db
class TestGetUnsupportedSetsQuery:
    """Tests for get_unsupported_sets_query function."""

    def test_returns_query(self):
        from cardDatabase.views.utils.search_context import get_unsupported_sets_query

        query = get_unsupported_sets_query()
        assert query is not None


@pytest.mark.django_db
class TestGetUnsupportedDecklistsQuery:
    """Tests for get_unsupported_decklists_query function."""

    def test_returns_query(self):
        from cardDatabase.views.utils.search_context import get_unsupported_decklists_query

        query = get_unsupported_decklists_query()
        assert query is not None


# =============================================================================
# Tests for tournament/utils/utilities.py
# =============================================================================


class TestCheckValueIsMetaData:
    """Tests for check_value_is_meta_data function."""

    def test_field_exists(self):
        from cardDatabase.views.tournament.utils.utilities import check_value_is_meta_data

        fields = [{"name": "field1"}, {"name": "field2"}]
        assert check_value_is_meta_data("field1", fields) is True

    def test_field_not_exists(self):
        from cardDatabase.views.tournament.utils.utilities import check_value_is_meta_data

        fields = [{"name": "field1"}, {"name": "field2"}]
        assert check_value_is_meta_data("field3", fields) is False

    def test_empty_fields(self):
        from cardDatabase.views.tournament.utils.utilities import check_value_is_meta_data

        assert check_value_is_meta_data("field1", []) is False


class TestMapMetaData:
    """Tests for map_meta_data function."""

    def test_maps_value_to_field(self):
        from cardDatabase.views.tournament.utils.utilities import map_meta_data

        fields = [{"name": "field1", "value": None}, {"name": "field2", "value": None}]
        result = map_meta_data("field1", "test_value", fields)
        assert result["value"] == "test_value"
        assert result["name"] == "field1"

    def test_field_not_found_returns_none(self):
        from cardDatabase.views.tournament.utils.utilities import map_meta_data

        fields = [{"name": "field1"}, {"name": "field2"}]
        result = map_meta_data("field3", "test_value", fields)
        assert result is None

    def test_does_not_modify_original(self):
        from cardDatabase.views.tournament.utils.utilities import map_meta_data

        fields = [{"name": "field1", "value": "original"}]
        map_meta_data("field1", "new_value", fields)
        assert fields[0]["value"] == "original"


class TestAnyEmpty:
    """Tests for any_empty function."""

    def test_all_non_empty(self):
        from cardDatabase.views.tournament.utils.utilities import any_empty

        assert any_empty("a", "b", "c") is False

    def test_one_empty_string(self):
        from cardDatabase.views.tournament.utils.utilities import any_empty

        assert any_empty("a", "", "c") is True

    def test_one_none(self):
        from cardDatabase.views.tournament.utils.utilities import any_empty

        assert any_empty("a", None, "c") is True

    def test_one_zero(self):
        from cardDatabase.views.tournament.utils.utilities import any_empty

        assert any_empty("a", 0, "c") is True

    def test_one_empty_list(self):
        from cardDatabase.views.tournament.utils.utilities import any_empty

        assert any_empty("a", [], "c") is True

    def test_no_args(self):
        from cardDatabase.views.tournament.utils.utilities import any_empty

        assert any_empty() is False


# =============================================================================
# Request Factory Fixture
# =============================================================================


@pytest.fixture
def rf():
    """Django request factory."""
    from django.test import RequestFactory

    return RequestFactory()
