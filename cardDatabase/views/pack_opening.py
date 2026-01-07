import json
import random

from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import Q
from django.shortcuts import render

from cardDatabase.models import Card
from cardDatabase.views.utils.search_context import (
    get_set_query,
    get_not_card_type_query,
    get_not_card_race_query,
    get_not_card_prefix_query,
    get_rarity_query,
    get_card_type_query,
    get_race_query,
    get_card_prefix_query,
    get_simple_set_query,
    get_not_set_query,
)


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
            pool_count = card_pool.count() - 1
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
            pool_count = card_pool.count() - 1
            # if pool_count < 1:
            #     return HttpResponse(str(json.dumps(pulledSlot)))
            pull = random.randrange(0, pool_count)
            card = card_pool[pull]
            pulls.append({"card": card, "slot": slot.lower()})
            pull_history.append({"slot": slot, "cardId": card.card_id})

    ctx = {"pull_history": pull_history, "valid": True, "pulls": pulls, "packImage": config["packImage"]}

    return render(request, "cardDatabase/html/pack_opening.html", ctx)


def read_file(path):
    with staticfiles_storage.open(path, "r") as file:
        data = file.read()
    return data


def weightSamples(pairs):
    rand = random.randrange(1, 100)
    segments = []
    for pair in pairs:
        for _ in range(pair["chance"]):
            segments.append(pair)

    return segments[rand]


def build_duplicate_filter(pull_history, slot):
    set_query = ~Q()
    for entry in pull_history:
        if entry["slot"] is slot:
            set_query &= ~Q(card_id=entry["cardId"])
    return set_query


def get_random_array_entry(array):
    rand = random.randrange(1, len(array))
    return array[rand]
