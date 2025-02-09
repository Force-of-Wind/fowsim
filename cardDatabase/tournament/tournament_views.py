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
from django.utils.dateparse import parse_datetime

from ..forms import SearchForm, AdvancedSearchForm, AddCardForm, UserRegistrationForm, DecklistSearchForm
from ..models.Tournament import Tournament, TournamentLevel, TournamentPlayer, TournamentStaff, StaffRole
from ..models.Banlist import Format
from fowsim import constants as CONS
from . import tournament_constants as TOURNAMENTCONS



def show_tournaments(request):
    tournaments = Tournament.objects.order_by('-start_datetime').all()

    return render(request, 'tournament/tournament_list.html', context={
        "tournaments": tournaments
    })

@login_required
def new_tournament(request):
    return render(request, 'tournament/tournament_create.html', context={
        'meta_data': TOURNAMENTCONS.TOURNAMENT_DEFAULT_META_DATA,
        'formats': Format.objects.all().order_by('pk'),
        'levels': TournamentLevel.objects.all()
    })



@login_required
def create_tournament(request):
    if not request.method == "POST":
        raise Http404
    data = json.loads(request.body.decode('UTF-8'))
    meta_data = []
    for fieldName in data:
        if check_value_is_meta_data(fieldName, TOURNAMENTCONS.TOURNAMENT_DEFAULT_META_DATA):
            meta_data[fieldName] = map_meta_data(fieldName, data[fieldName], TOURNAMENTCONS.TOURNAMENT_DEFAULT_META_DATA)
    
    title = data['title']

    is_online = False
    if 'is_online' in data:
        is_online = True

    format_id = data['format']
    level_id = data['level']

    start_date_time = parse_datetime(data['start_date_time'])
    registration_deadline = parse_datetime(data['deck_registration_end_date_time'])
    deck_edit_deadline = None

    if 'deck_lock_date_time' in data:
        deck_edit_deadline = parse_datetime(data['deck_lock_date_time'])

    tournament = Tournament.objects.create(
        title=title,
        is_online = is_online,
        format = Format.objects.get(pk=format_id),
        level = TournamentLevel.objects.get(pk=level_id),
        start_date_time = start_date_time,
        registration_deadline = registration_deadline,
        deck_edit_deadline = deck_edit_deadline
    )

    TournamentStaff.objects.create(tournament=tournament, profile=request.user.profile, role=StaffRole.objects.get(default=True))

    return HttpResponseRedirect(reverse('cardDatabase-tournament-admin', kwargs={'tournament_id': tournament.id}))

def check_value_is_meta_data(name, default_meta_data_fields):
    for field in default_meta_data_fields:
        if field['name'] == name:
            return True
    return False

def map_meta_data(name, value, default_meta_data_fields):
    for field in default_meta_data_fields:
        if field['name'] == name:
            field['value'] = value
            return field
    return None

@login_required
def edit_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    staffAccount = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staffAccount is None or not staffAccount.role.canWrite:
        return HttpResponse('Not authorized', 401)
    
    if not request.method == "POST":
        raise Http404
    data = json.loads(request.body.decode('UTF-8'))
    meta_data = []
    for fieldName in data:
        if check_value_is_meta_data(fieldName, TOURNAMENTCONS.TOURNAMENT_DEFAULT_META_DATA):
            meta_data[fieldName] = map_meta_data(fieldName, data[fieldName], TOURNAMENTCONS.TOURNAMENT_DEFAULT_META_DATA)
    
    title = data['title']

    is_online = False
    if 'is_online' in data:
        is_online = True

    format_id = data['format']
    level_id = data['level']

    start_date_time = parse_datetime(data['start_date_time'])
    registration_deadline = parse_datetime(data['deck_registration_end_date_time'])
    deck_edit_deadline = None

    if 'deck_lock_date_time' in data:
        deck_edit_deadline = parse_datetime(data['deck_lock_date_time'])

    tournament.title=title
    tournament.is_online = is_online
    tournament.format = Format.objects.get(pk=format_id)
    tournament.level = TournamentLevel.objects.get(pk=level_id)
    tournament.start_date_time = start_date_time
    tournament.registration_deadline = registration_deadline
    tournament.deck_edit_deadline = deck_edit_deadline

    return HttpResponseRedirect(reverse('cardDatabase-tournament-admin', kwargs={'tournament_id': tournament.id}))

def tournament_detail(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    return render(request, 'tournament/tournament_detail.html', context={
        'tournament': tournament
    })

@login_required
def tournament_admin(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    staffAccount = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staffAccount is None or not staffAccount.role.canDelete:
        return HttpResponse('Not authorized', 401)

    return render(request, 'tournament/tournament_admin.html', context={
        'tournament': tournament
    })

@login_required
def delete_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    staffAccount = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staffAccount is None or not staffAccount.role.canDelete:
        return HttpResponse('Not authorized', 401)
    
    tournament.delete()

    return HttpResponseRedirect(reverse('cardDatabase-tournament-list'))