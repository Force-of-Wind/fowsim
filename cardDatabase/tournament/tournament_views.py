import json
import re
import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, F, Count
from django.forms.fields import MultipleChoiceField
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404
from django.urls import reverse

from ..forms import SearchForm, AdvancedSearchForm, AddCardForm, UserRegistrationForm, DecklistSearchForm
from ..models.Tournament import Tournament, TournamentLevel, TournamentPlayer, TournamentStaff, StaffRole
from ..models.Banlist import Format
from fowsim import constants as CONS



def show_tournaments(request):
    tournaments = Tournament.objects.order_by('-start_datetime').all()

    return render(request, 'tournament/tournament_list.html', context={
        "tournaments": tournaments
    })

@login_required
def new_tournament(request):
    return render(request, 'tournament/tournament_create.html', context={
        'formats': Format.objects.all(),
        'levels': TournamentLevel.objects.all()
    })

@login_required
def create_tournament(request):

    #create tournament with GET DATA

    return render(request, 'tournament/tournament_details.html', context={
        #'tournament'
    })

