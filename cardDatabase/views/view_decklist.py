from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone

from cardDatabase.models import DeckList, BannedCard, CombinationBannedCards, TournamentPlayer
from cardDatabase.models.CardType import Card
from cardDatabase.models.DeckList import UserDeckListZone
from cardDatabase.models.Rulings import Restriction, RestrictionException
from django.db.models import Q, Prefetch

from fowsim import constants as CONS


def _build_other_sides_map(cards_qs):
    """Batch-compute other_sides for all cards in the deck in a single query."""
    other_sides_map = {}  # card.id -> list of Card objects
    other_side_q = Q()
    card_lookup = {}  # potential_card_id -> list of source card ids

    for deck_card in cards_qs:
        card = deck_card.card
        shared_number = card.set_number
        if not shared_number:
            other_sides_map[card.id] = []
            continue

        self_other_side_char = ""
        for to_remove in CONS.OTHER_SIDE_CHARACTERS:
            if to_remove in shared_number:
                shared_number = shared_number.replace(to_remove, "")
                self_other_side_char = to_remove

        shared_id = card.set_code + "-" + shared_number

        potential_ids = []
        if self_other_side_char:
            potential_ids.append(shared_id)
        for to_query in CONS.OTHER_SIDE_CHARACTERS:
            if to_query != self_other_side_char:
                potential_ids.append(shared_id + to_query)

        for pid in potential_ids:
            other_side_q |= Q(card_id=pid)
            card_lookup.setdefault(pid, []).append(card.id)

        other_sides_map[card.id] = []

    if other_side_q:
        for other_card in Card.objects.filter(other_side_q):
            for source_id in card_lookup.get(other_card.card_id, []):
                other_sides_map[source_id].append(other_card)

    return other_sides_map


def get(request, decklist_id, share_parameter=""):
    decklist = get_object_or_404(
        DeckList.objects.select_related("profile__user", "deck_format"),
        pk=decklist_id,
    )
    if (not decklist.public and not request.user == decklist.profile.user and not request.user.is_superuser) and (
        share_parameter == "" or not decklist.shareCode == share_parameter
    ):
        return HttpResponseRedirect(reverse("cardDatabase-private-decklist"))

    cards = list(
        decklist.cards.select_related(
            "card", "zone__zone",
        ).prefetch_related("card__tag").all()
    )
    zones = (
        UserDeckListZone.objects.filter(decklist=decklist)
        .order_by("position")
        .values_list("zone__name", flat=True)
        .distinct()
    )

    """
    DeckListCard is not the same as Card so compare the pk's by using values_list to get Card objects from DeckListCard
    Also avoids duplicate named/reprinted cards needing multiple banlist entries
    """
    deck_card_names = [c.card.name for c in cards]

    if decklist.deck_format.name != CONS.PARADOX_FORMAT:
        banned_cards = BannedCard.objects.select_related("card").filter(format=decklist.deck_format)
        combination_bans = CombinationBannedCards.objects.prefetch_related("cards").filter(format=decklist.deck_format)
    else:
        query = Q(format=decklist.deck_format)
        query |= Q(format__name=CONS.WANDERER_FORMAT)
        banned_cards = BannedCard.objects.select_related("card").filter(query)
        combination_bans = CombinationBannedCards.objects.prefetch_related("cards").filter(query)

    ban_warnings = []
    for banned_card in banned_cards:
        if banned_card.card.name in deck_card_names:
            ban_warnings.append(
                {
                    "format": decklist.deck_format.name,
                    "card": banned_card.card.name,
                    "card_img_url": banned_card.card.card_image.url,
                    "view_card_url": reverse("cardDatabase-view-card", kwargs={"card_id": banned_card.card.card_id}),
                }
            )

    combination_ban_warnings = []
    for combination_ban in combination_bans:
        combination_banned_cards = combination_ban.cards.all()
        combination_banned_card_names = [c.name for c in combination_banned_cards]
        overlap = set(combination_banned_card_names) & set(deck_card_names)
        if len(overlap) > 1:
            combination_ban_warning = {
                "format": decklist.deck_format.name,
                "cards": [],
            }
            for card in combination_banned_cards:
                if card.name in overlap:
                    combination_ban_warning["cards"].append(
                        {
                            "name": card.name,
                            "image_url": card.card_image.url,
                            "view_card_url": reverse("cardDatabase-view-card", kwargs={"card_id": card.card_id}),
                        }
                    )
            combination_ban_warnings.append(combination_ban_warning)

    restrictions = Restriction.objects.select_related(
        "action", "tag", "restricted_tag",
    ).prefetch_related(
        Prefetch(
            "restrictionexception_set",
            queryset=RestrictionException.objects.select_related(
                "exception_applying_card", "exception_action",
            ).prefetch_related("exception_action__applying_to_cards"),
        ),
    ).all()
    deck_restrictions = []
    for restriction in restrictions:
        deck_exceptions = []
        for exception in restriction.restrictionexception_set.all():
            cards_exception_applies_to = [card.id for card in exception.exception_action.applying_to_cards.all()]
            deck_exceptions.append(
                {
                    "exceptionApplyingCard": exception.exception_applying_card.id,
                    "exceptionApplyingZone": exception.card_zone_restriction,
                    "exceptionAction": exception.exception_action.technical_name,
                    "cardExceptionAppliesTo": cards_exception_applies_to,
                }
            )

        deck_restrictions.append(
            {
                "text": restriction.text,
                "action": restriction.action.technical_name,
                "checkingTag": restriction.tag.id,
                "restrictedTag": restriction.restricted_tag.id,
                "exceptions": deck_exceptions,
            }
        )

    # Batch-compute other sides for all cards (avoids N+1 in template)
    other_sides_map = _build_other_sides_map(cards)

    cardsData = []
    for card in cards:
        tags = [tag.id for tag in card.card.tag.all()]
        cardsData.append({"quantity": card.quantity, "tags": tags, "id": card.card.id, "zone": card.zone.zone.name})

    absolute_share_link = None
    deck_share_user_managed = True
    deck_lock_user_managed = True

    if not (decklist.shareCode is None) and decklist.shareCode:
        relative_share_link = reverse(
            "cardDatabase-view-decklist-share",
            kwargs={"decklist_id": decklist.pk, "share_parameter": decklist.shareCode},
        )
        absolute_share_link = request.build_absolute_uri(relative_share_link)

    if not (decklist.shareMode is None) and not (decklist.shareMode == CONS.MODE_PRIVATE):
        deck_share_user_managed = False

    if not (decklist.deck_lock is None) and not (decklist.deck_lock == CONS.MODE_PRIVATE):
        deck_lock_user_managed = False

    deck_tournament_locked = False
    tournament_player = None
    if request.user.is_authenticated:
        tournament_player = TournamentPlayer.objects.select_related("tournament").filter(profile=request.user.profile, deck=decklist).first()

    if tournament_player is not None:
        tournament = tournament_player.tournament
        deck_edit_locked = tournament.deck_edit_locked

        over_edit_deadline = True
        if (
            tournament.deck_edit_deadline is None
            or tournament.deck_edit_deadline.timestamp() > timezone.now().timestamp()
        ):
            over_edit_deadline = False

        if deck_edit_locked or over_edit_deadline:
            deck_tournament_locked = True

    return render(
        request,
        "cardDatabase/html/view_decklist.html",
        context={
            "decklist": decklist,
            "zones": zones,
            "cards": cards,
            "ban_warnings": ban_warnings,
            "combination_ban_warnings": combination_ban_warnings,
            "deckRestrictions": deck_restrictions,
            "cardsData": cardsData,
            "other_sides_map": other_sides_map,
            "absoluteShareLink": absolute_share_link,
            "deckLockUserManaged": deck_lock_user_managed,
            "deckShareUserManaged": deck_share_user_managed,
            "deckTournamentLocked": deck_tournament_locked,
            "tournamentDeck": tournament_player is not None,
        },
    )
