import json

from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from cardDatabase.forms import AdvancedSearchForm
from cardDatabase.views.utils.search_context import advanced_search
from fowsim.decorators import reddit_bot
from fowsim import constants as CONS


@csrf_exempt
@require_POST
@reddit_bot
def get(request):
    try:
        data = json.loads(request.body.decode("UTF-8"))
    except (json.JSONDecodeError, json.decoder.JSONDecodeError):
        return HttpResponse("Error loading json", status=401)
    words = data.get("keywords", None)
    if not words:
        return HttpResponse("No keywords provided", status=400)
    flags = data.get("flags", [])

    exact_query = False
    if "e" in flags:
        exact_query = True

    all_sides = False
    if "b" in flags:
        all_sides = True

    reverse_sort = False
    if "a" in flags:
        reverse_sort = True

    adv_form = AdvancedSearchForm(request.POST)
    if not adv_form.is_valid():  # Have to run is_valid to access cleaned_data
        return HttpResponse("Unknown error occured", status=500)
    adv_form.cleaned_data["generic_text"] = " ".join(words)
    adv_form.cleaned_data["text_exactness"] = CONS.TEXT_EXACT if exact_query else CONS.TEXT_CONTAINS_ALL
    adv_form.cleaned_data["sort_by"] = CONS.DATABASE_SORT_BY_MOST_RECENT
    adv_form.cleaned_data["reverse_sort"] = reverse_sort
    adv_form.cleaned_data["text_search_fields"] = ["name"]
    cards = advanced_search(adv_form)
    ctx = {"cards": []}
    card = None
    if len(cards["cards"]):
        card = cards["cards"][0]
    if card:
        ctx["cards"].append(
            {
                "name": card.name,
                "image_url": request.build_absolute_uri(card.card_image.url),
                "view_card_url": request.build_absolute_uri(
                    reverse("cardDatabase-view-card", kwargs={"card_id": card.card_id})
                ),
            }
        )
        if all_sides:
            for other_side in card.other_sides:
                ctx["cards"].append(
                    {
                        "name": other_side.name,
                        "image_url": request.build_absolute_uri(other_side.card_image.url),
                        "view_card_url": request.build_absolute_uri(
                            reverse("cardDatabase-view-card", kwargs={"card_id": other_side.card_id})
                        ),
                    }
                )

    return JsonResponse(ctx)
