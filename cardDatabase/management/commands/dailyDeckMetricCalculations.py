import datetime

from django.core.management.base import BaseCommand
from django.db.models import Count, Sum, Q
from django.utils import timezone

from cardDatabase.models.Metrics import PickPeriod, MostPickedCardPickRate, AttributePickRate, CardTotalCostPickRate, CardTypePickRate
from cardDatabase.models.DeckList import DeckListCard, DeckList
from cardDatabase.models.CardType import Card, CardColour, Type


def delete_existing_metrics():
    MostPickedCardPickRate.objects.all().delete()
    AttributePickRate.objects.all().delete()
    CardTotalCostPickRate.objects.all().delete()
    CardTypePickRate.objects.all().delete()


class Command(BaseCommand):
    help = 'Runs daily and recreates all Metric model values found in cardDatabase.models.Metrics.py'

    def handle(self, *args, **options):
        pick_periods = PickPeriod.objects.all()
        delete_existing_metrics()
        for period in pick_periods:
            if period.all_time:
                cards = Card.objects.filter(decklistcard__isnull=False).annotate(number_of_decks=Count('decklistcard')).order_by('-number_of_decks')
                decklists = DeckList.objects.all()
            else:
                period_dt = timezone.now() - datetime.timedelta(days=period.days)
                cards = Card.objects.filter(decklistcard__decklist__last_modified__gte=period_dt)
                decklists = DeckList.objects.filter(last_modified__gte=period_dt)
                #  Sets number_of_decks to be an integer of the number of decks that there exists at least 1 of the card
                cards = cards.annotate(
                    number_of_decks=Count('decklistcard__decklist__id',filter=Q(decklistcard__decklist__last_modified__gte=period_dt), distinct=True)
                ).filter(number_of_decks__gte=1).order_by('-number_of_decks')

            deck_counts = decklists.count()
            for card in cards[:30]:
                MostPickedCardPickRate.objects.create(card=card, percentage=int(card.number_of_decks * 100 / deck_counts), period=period)

            deck_cards = DeckListCard.objects.filter(decklist__in=decklists)
            total_cards = deck_cards.aggregate(Sum('quantity'))['quantity__sum'] or 0
            if total_cards:
                for card_attr in CardColour.objects.all():
                    attr_cards = deck_cards.filter(card__colours=card_attr)
                    attr_count = attr_cards.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    AttributePickRate.objects.create(period=period, card_attr=card_attr, percentage=int(attr_count * 100 / total_cards))

                for card_type in Type.objects.all():
                    type_cards = deck_cards.filter(card__types=card_type)
                    type_count = type_cards.aggregate(Sum('quantity'))['quantity__sum'] or 0
                    CardTypePickRate.objects.create(period=period, card_type=card_type, percentage=int(type_count * 100 / total_cards))

                total_costs = [0] * 13
                for card in deck_cards:
                    total_costs[card.card.total_cost] += card.quantity

                for i in range(0, 13):
                    CardTotalCostPickRate.objects.create(period=period, percentage=int(total_costs[i] * 100 / total_cards), total_cost=i)


