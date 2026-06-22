import functools
import json
import random

from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import Max, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from cardDatabase.models import Card, DeckList, TournamentPlayer
from cardDatabase.models.DeckList import DeckListCard, DeckListZone, UserDeckListZone
from cardDatabase.views.utils.search_context import (
    get_card_prefix_query,
    get_card_type_query,
    get_not_card_prefix_query,
    get_not_card_race_query,
    get_not_card_type_query,
    get_not_set_query,
    get_race_query,
    get_rarity_query,
    get_set_query,
    get_simple_set_query,
)
from fowsim import constants as CONS

SESSION_SKIP_ANIMATION_KEY = "pack_skip_animation"

_DEFAULT_ZONE = "Main Deck"

#  Map the database card type groups to the deck zones cards should land in by default.
#  "Other Decks" (Rune / Master Rune / Extension Rule) has no dedicated deck zone in this
#  app, so those types fall back to the Main Deck.
_CARD_TYPE_GROUP_TO_ZONE = {
    "Main Deck": "Main Deck",
    "J/Ruler": "Ruler Area",
    "Magic Stone Deck": "Magic Stone Deck",
    "Other Decks": _DEFAULT_ZONE,
}


def _ajax_login_required(view):
    """Like @login_required but returns a JSON 401 instead of redirecting to the login page.

    The pack opener calls these endpoints over AJAX expecting JSON, so a 302 to the HTML
    login page would surface as an opaque parse error if the session has expired.
    """

    @functools.wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "authentication_required"}, status=401)
        return view(request, *args, **kwargs)

    return wrapped


def _parse_json_body(request):
    """Parse a JSON request body, returning None on malformed/empty input."""
    try:
        return json.loads(request.body.decode("UTF-8"))
    except (ValueError, UnicodeDecodeError):
        return None


def _build_card_type_to_zone():
    mapping = {}
    for group in CONS.DATABASE_CARD_TYPE_GROUPS:
        zone = _CARD_TYPE_GROUP_TO_ZONE.get(group["name"], _DEFAULT_ZONE)
        for card_type in group["types"]:
            mapping[card_type] = zone
    return mapping


CARD_TYPE_TO_ZONE = _build_card_type_to_zone()


def suggest_zone_for_card(card):
    for card_type in card.types.all():
        zone = CARD_TYPE_TO_ZONE.get(card_type.name)
        if zone is not None:
            return zone
    return _DEFAULT_ZONE


def get(request, setcode=None):
    if setcode is None:
        return render(request, "cardDatabase/html/pack_opening.html", {"valid": False})
    pathToConfig = "pack_config/" + setcode.lower() + ".json"
    try:
        config = json.loads(read_file(pathToConfig))
    except FileNotFoundError:
        return render(request, "cardDatabase/html/pack_opening.html", {"valid": False})

    slots = config["slots"]
    pulls = []

    pull_history = []

    for slot in slots:
        if "card_override" in config:
            card = None
            card_overrides = config["card_override"]
            for override in card_overrides:
                if len(pull_history) > 0:
                    last_pulled_card = pull_history[-1]
                    if override["rarity"] == slot and last_pulled_card["cardId"] == override["previousCardId"]:
                        card_id = ""
                        if "newCardIds" in override:
                            card_id = get_random_array_entry(override["newCardIds"])

                        if "newCardId" in override:
                            card_id = override["newCardId"]

                        if card_id != "":
                            card = (Card.objects.filter(Q(card_id=card_id)).distinct())[0]
                            pulls.append({"card": card, "slot": slot.lower()})
                            pull_history.append({"slot": slot, "cardId": card.card_id})
            if card is not None:
                continue

        set_query = get_set_query([setcode.upper()])
        if "set_override" in config:
            set_overrides = config["set_override"]
            for override in set_overrides:
                if override["rarity"] == slot:
                    set_query = get_set_query(override["setCodes"])

        card_pool = Card.objects.filter(build_duplicate_filter(pull_history, slot)).distinct()

        if "excludes" in config:
            excludes = config["excludes"]
            for exclude in excludes:
                if exclude["rarity"] == slot:
                    if "type" in exclude:
                        excluded_card_types = exclude["type"]
                        card_type_query = get_not_card_type_query(excluded_card_types)
                        card_pool = card_pool.filter(card_type_query)

                    if "races" in exclude:
                        excluded_card_races = exclude["races"]
                        card_type_query = get_not_card_race_query(excluded_card_races)
                        card_pool = card_pool.filter(card_type_query)

                    if "cardIdPrefix" in exclude:
                        excluded_card_id_prefix = exclude["cardIdPrefix"]
                        card_prefix_query = get_not_card_prefix_query(excluded_card_id_prefix)
                        card_pool = card_pool.filter(card_prefix_query)

        if not slot in config:
            rarity_query = get_rarity_query([slot])
            card_pool = card_pool.filter(rarity_query).filter(set_query)
            pool_count = card_pool.count()
            if pool_count == 0:
                continue
            pull = random.randrange(0, pool_count)
            card = card_pool[pull]
            pulls.append({"card": card, "slot": slot.lower()})
            pull_history.append({"slot": slot, "cardId": card.card_id})

        else:
            slotConfig = config[slot]
            if len(slotConfig) >= 2:
                pulledSlot = weightSamples(slotConfig)
            else:
                pulledSlot = slotConfig[0]
            if "rarity" in pulledSlot and pulledSlot["rarity"] is not None:
                rarity_query = get_rarity_query([pulledSlot["rarity"]])
                card_pool = card_pool.filter(rarity_query)
            if "conditions" in pulledSlot:
                for condition in pulledSlot["conditions"]:
                    equalsCriteria = condition["equals"]
                    if "type" in condition:
                        filter_type = condition["type"]
                        if equalsCriteria:
                            card_type_query = get_card_type_query([filter_type])
                            card_pool = card_pool.filter(card_type_query)
                        else:
                            card_type_query = get_not_card_type_query([filter_type])
                            card_pool = card_pool.filter(card_type_query)
                    if "races" in condition:
                        filter_race = condition["races"]
                        if equalsCriteria:
                            card_type_query = get_race_query(filter_race)
                            card_pool = card_pool.filter(card_type_query)
                        else:
                            card_type_query = get_not_card_race_query(filter_race)
                            card_pool = card_pool.filter(card_type_query)
                    if "cardIdPrefix" in condition:
                        card_id_prefix = condition["cardIdPrefix"]
                        if equalsCriteria:
                            card_id_prefix_query = get_card_prefix_query(card_id_prefix)
                            card_pool = card_pool.filter(card_id_prefix_query)
                        else:
                            card_id_prefix_query = get_not_card_prefix_query(card_id_prefix)
                            card_pool = card_pool.filter(card_id_prefix_query)
                    if "setOverrides" in condition:
                        set_overrides = condition["setOverrides"]
                        if equalsCriteria:
                            set_query = get_simple_set_query(set_overrides)
                        else:
                            set_query = get_not_set_query(set_overrides)

            card_pool = card_pool.filter(set_query)
            pool_count = card_pool.count()
            if pool_count == 0:
                continue
            pull = random.randrange(0, pool_count)
            card = card_pool[pull]
            pulls.append({"card": card, "slot": slot.lower()})
            pull_history.append({"slot": slot, "cardId": card.card_id})

    #  Resolve every pulled card's types in a single query rather than one per card.
    cards_with_types = Card.objects.filter(pk__in=[pull["card"].pk for pull in pulls]).prefetch_related("types")
    zone_by_pk = {card.pk: suggest_zone_for_card(card) for card in cards_with_types}
    for pull in pulls:
        pull["zone_suggestion"] = zone_by_pk.get(pull["card"].pk, _DEFAULT_ZONE)

    ctx = {
        "pull_history": pull_history,
        "valid": True,
        "pulls": pulls,
        "packImage": config["packImage"],
        "deck_zones": CONS.ZONES_SHOWN_BY_DEFAULT,
        "skip_animation": bool(request.session.get(SESSION_SKIP_ANIMATION_KEY, False)),
        "setcode": setcode.upper(),
    }

    return render(request, "cardDatabase/html/pack_opening.html", ctx)


def read_file(path):
    with staticfiles_storage.open(path, "r") as file:
        data = file.read()
    return data


def weightSamples(pairs):
    segments = []
    for pair in pairs:
        for _ in range(pair["chance"]):
            segments.append(pair)

    return random.choice(segments)


def build_duplicate_filter(pull_history, slot):
    set_query = ~Q()
    for entry in pull_history:
        if entry["slot"] is slot:
            set_query &= ~Q(card_id=entry["cardId"])
    return set_query


def get_random_array_entry(array):
    return random.choice(array)


@require_POST
def set_skip_preference(request):
    """Persist the 'always skip the opening animation' preference on the session."""
    data = _parse_json_body(request)
    if data is None:
        return HttpResponse("Invalid request body.", status=400)
    request.session[SESSION_SKIP_ANIMATION_KEY] = bool(data.get("skip", False))
    return JsonResponse({"skip": request.session[SESSION_SKIP_ANIMATION_KEY]})


@_ajax_login_required
def user_decks(request):
    """Return the current user's editable, non-tournament decks so pulled cards can be added to one."""
    decks = (
        DeckList.objects.filter(profile__user=request.user)
        .exclude(deck_lock=CONS.MODE_TOURNAMENT)
        .exclude(tournamentplayer__isnull=False)  # exclude decks registered to a tournament
        .order_by("-last_modified")
        .distinct()
    )
    return JsonResponse({"decks": [{"id": deck.pk, "name": deck.name} for deck in decks]})


def _deck_is_editable(decklist):
    """Pack pulls may only be added to plain, non-tournament decks."""
    if decklist.deck_lock == CONS.MODE_TOURNAMENT:
        return False

    if TournamentPlayer.objects.filter(deck=decklist).exists():
        return False

    return True


@_ajax_login_required
@require_POST
def add_to_deck(request):
    """Add one or more pulled cards to a user's deck, into the requested zone."""
    data = _parse_json_body(request)
    if data is None:
        return HttpResponse("Invalid request body.", status=400)
    decklist = get_object_or_404(DeckList, pk=data.get("decklist_id"), profile__user=request.user)

    if not _deck_is_editable(decklist):
        return HttpResponse("Tournament decks cannot be modified from the pack opener.", status=400)

    added = 0
    for entry in data.get("cards", []):
        card = Card.objects.filter(card_id=entry.get("card_id")).first()
        if card is None:
            continue

        #  Only allow the zones the UI offers; never let a crafted request mint arbitrary
        #  rows in the shared DeckListZone table.
        zone_name = entry.get("zone")
        if zone_name not in CONS.ZONES_SHOWN_BY_DEFAULT:
            zone_name = _DEFAULT_ZONE
        zone, _ = DeckListZone.objects.get_or_create(name=zone_name)

        user_zone = UserDeckListZone.objects.filter(decklist=decklist, zone=zone).first()
        if user_zone is None:
            next_zone_position = (
                UserDeckListZone.objects.filter(decklist=decklist).aggregate(Max("position"))["position__max"]
            )
            next_zone_position = 0 if next_zone_position is None else next_zone_position + 1
            user_zone = UserDeckListZone.objects.create(decklist=decklist, zone=zone, position=next_zone_position)

        deck_card = DeckListCard.objects.filter(decklist=decklist, card=card, zone=user_zone).first()
        if deck_card is not None:
            deck_card.quantity += 1
            deck_card.save()
        else:
            next_card_position = (
                DeckListCard.objects.filter(decklist=decklist).aggregate(Max("position"))["position__max"]
            )
            next_card_position = 0 if next_card_position is None else next_card_position + 1
            DeckListCard.objects.create(
                decklist=decklist, card=card, zone=user_zone, position=next_card_position, quantity=1
            )
        added += 1

    decklist.save()  # refresh last_modified
    return JsonResponse({"success": True, "added": added, "decklist_id": decklist.pk})
