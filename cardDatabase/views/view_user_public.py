from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Sum

from cardDatabase.models import DeckList, Format
from cardDatabase.forms import DecklistSearchForm
from cardDatabase.views.utils.search_context import (
    get_form_from_params,
    get_unsupported_decklists_query,
    apply_deckcard_cardname_search,
    get_deck_format_query,
)
from fowsim import constants as CONS


def get(request, username=None):
    # Redirect if no username provided
    if username is None:
        return redirect("cardDatabase-view-users-decklist", username=request.user.username)

    # Get the user being viewed
    user = get_object_or_404(User, username=username)
    is_owner = request.user == user

    # Get search form from query parameters
    decklist_form = get_form_from_params(DecklistSearchForm, request)

    # Start with base queryset
    decklists = DeckList.objects.filter(profile=User.objects.get(username=username).profile).distinct()

    # If not owner, only show public decklists
    if not is_owner:
        decklists = decklists.exclude(get_unsupported_decklists_query())

    # Apply search and filters if form is valid
    if decklist_form.is_valid() and request.GET.get("form_type") == "decklist-form":
        # Apply format filter
        deck_format_filter = get_deck_format_query(decklist_form.cleaned_data["deck_format"])
        decklists = decklists.filter(deck_format_filter)

        # Apply card name search
        search_text = decklist_form.cleaned_data["contains_card"]
        text_exactness = decklist_form.cleaned_data["text_exactness"]
        decklists = apply_deckcard_cardname_search(decklists, search_text, ["name"], text_exactness)

    # Apply sorting
    sort_by = request.GET.get("sort_by", CONS.DECKLIST_SORT_BY_LAST_MODIFIED)
    reverse_sort = request.GET.get("reverse_sort") == "true"

    decklists = sort_decklists(decklists, sort_by, reverse_sort)

    # Paginate results
    paginator = Paginator(decklists, CONS.DECKLIST_PAGE_SIZE)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)
    page_range = paginator.get_elided_page_range(number=page_number, on_each_side=1, on_ends=1)

    # Get formats for form
    formats = Format.objects.all()

    context = {
        "decklists": page_obj,
        "page_range": page_range,
        "is_owner": is_owner,
        "formats": formats,
        "decklist_form": decklist_form,
        "viewed_user": user,
        "total_results": paginator.count,
        "sort_choices": CONS.DECKLIST_SORT_BY_CHOICES,
    }

    return render(request, "cardDatabase/html/user_decklists.html", context)


def sort_decklists(decklists, sort_by, is_reversed):
    """Sort decklists by selected field and direction."""
    if sort_by == CONS.DECKLIST_SORT_BY_LAST_MODIFIED:
        field = "-last_modified" if not is_reversed else "last_modified"
    elif sort_by == CONS.DECKLIST_SORT_BY_NAME:
        field = "name" if not is_reversed else "-name"
    elif sort_by == CONS.DECKLIST_SORT_BY_CARD_COUNT:
        # Annotate with total card count, then sort
        decklists = decklists.annotate(total_cards=Sum("cards__quantity"))
        field = "-total_cards" if not is_reversed else "total_cards"
        return decklists.order_by(field)
    else:
        field = "-last_modified"  # Default

    return decklists.order_by(field)
