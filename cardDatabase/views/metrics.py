from django.shortcuts import render

from cardDatabase.models import (
    MostPickedCardPickRate,
    AttributePickRate,
    CardTotalCostPickRate,
    CardTypePickRate,
    PickPeriod,
)


def get(request):
    ctx = {
        "most_picked_cards": MostPickedCardPickRate.objects.all().order_by("-percentage"),
        "attribute_picks": AttributePickRate.objects.all().order_by("-percentage"),
        "total_cost_picks": CardTotalCostPickRate.objects.all().order_by("-total_cost"),
        "card_type_picks": CardTypePickRate.objects.all().order_by("-percentage"),
        "pick_periods": PickPeriod.objects.all(),
    }
    return render(request, "cardDatabase/html/metrics.html", ctx)
