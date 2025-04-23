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

from ...forms import SearchForm, AdvancedSearchForm, AddCardForm, UserRegistrationForm, DecklistSearchForm
from ...models.Tournament import Tournament, TournamentLevel, TournamentPlayer, TournamentStaff, StaffRole
from ...models.Banlist import Format
from fowsim import constants as CONS
from . import tournament_constants as TOURNAMENTCONS



def show_tournaments(request):
    tournaments = Tournament.objects.order_by('-start_datetime').all()

    return render(request, 'tournament/tournament_list.html', context={
        "tournaments": tournaments
    })

@login_required
def new_tournament(request, error = False):
    return render(request, 'tournament/tournament_create.html', context={
        'meta_data': TOURNAMENTCONS.TOURNAMENT_DEFAULT_META_DATA,
        'formats': Format.objects.all().order_by('pk'),
        'levels': TournamentLevel.objects.all(),
        'error': error
    })

@login_required
def create_tournament(request):
    if not request.method == "POST":
        raise Http404
    data = dict(request.POST)
    meta_data = []
    for fieldName, _ in data.items():
        if check_value_is_meta_data(fieldName, TOURNAMENTCONS.TOURNAMENT_DEFAULT_META_DATA):
            meta_data.append(map_meta_data(fieldName, data.get(fieldName, [None])[0], TOURNAMENTCONS.TOURNAMENT_DEFAULT_META_DATA))
    
    title = request.POST.get('title')

    is_online = 'is_online' in data

    format_id = request.POST.get('format')
    level_id = request.POST.get('level')

    start_date_time = parse_datetime(request.POST.get('start_date_time'))
    registration_deadline = parse_datetime(request.POST.get('deck_registration_end_date_time'))
    deck_edit_deadline = None

    if 'deck_lock_date_time' in data:
        deck_edit_deadline = parse_datetime(request.POST.get('deck_lock_date_time'))
    

    if deck_edit_deadline is None:
        deck_edit_deadline = start_date_time
        

    if any_empty(title, meta_data, format_id, level_id, start_date_time, registration_deadline, deck_edit_deadline):
        return HttpResponseRedirect(reverse('cardDatabase-new-tournament',  kwargs={'error': True}))

    tournament = Tournament.objects.create(
        title=title,
        meta_data = meta_data,
        is_online = is_online,
        format = Format.objects.get(pk=format_id),
        level = TournamentLevel.objects.get(pk=level_id),
        start_datetime = start_date_time,
        registration_deadline = registration_deadline,
        deck_edit_deadline = deck_edit_deadline,
    )

    TournamentStaff.objects.create(tournament=tournament, profile=request.user.profile, role=StaffRole.objects.get(default=True))

    return HttpResponseRedirect(reverse('cardDatabase-admin-tournament', kwargs={'tournament_id': tournament.id}))

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

def any_empty(*args):
    return any(not arg for arg in args)

@login_required
def edit_tournament(request, tournament_id, error = False):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    staffAccount = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staffAccount is None or not staffAccount.role.can_write:
        return HttpResponse('Not authorized', 401)
    
    return render(request, 'tournament/tournament_edit.html', context={
        'meta_data': tournament.meta_data,
        'formats': Format.objects.all().order_by('pk'),
        'levels': TournamentLevel.objects.all(),
        'tournament': tournament,
        'error': error
    })

@login_required
def update_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    staffAccount = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staffAccount is None or not staffAccount.role.can_write:
        return HttpResponse('Not authorized', 401)
        
    
    if not request.method == "POST":
        raise Http404
    data = dict(request.POST)
    meta_data = []
    for fieldName, _ in data.items():
        if check_value_is_meta_data(fieldName, TOURNAMENTCONS.TOURNAMENT_DEFAULT_META_DATA):
            meta_data.append(map_meta_data(fieldName, data.get(fieldName, [None])[0], TOURNAMENTCONS.TOURNAMENT_DEFAULT_META_DATA))
    
    title = request.POST.get('title')

    is_online = 'is_online' in data

    format_id = request.POST.get('format')
    level_id = request.POST.get('level')

    start_date_time = parse_datetime(request.POST.get('start_date_time'))
    registration_deadline = parse_datetime(request.POST.get('deck_registration_end_date_time'))
    deck_edit_deadline = None

    if 'deck_lock_date_time' in data:
        deck_edit_deadline = parse_datetime(request.POST.get('deck_lock_date_time'))
    

    if deck_edit_deadline is None:
        deck_edit_deadline = start_date_time
        

    if any_empty(title, meta_data, format_id, level_id, start_date_time, registration_deadline, deck_edit_deadline):
        return HttpResponseRedirect(reverse('cardDatabase-edit-tournament',  kwargs={'error': True, 'tournament_id': tournament_id}))

    tournament.title=title
    tournament.is_online = is_online
    tournament.format = Format.objects.get(pk=format_id)
    tournament.level = TournamentLevel.objects.get(pk=level_id)
    tournament.start_datetime = start_date_time
    tournament.registration_deadline = registration_deadline
    tournament.deck_edit_deadline = deck_edit_deadline
    tournament.meta_data = meta_data
    tournament.save()

    return HttpResponseRedirect(reverse('cardDatabase-admin-tournament', kwargs={'tournament_id': tournament.id}))

def tournament_detail(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    return render(request, 'tournament/tournament_detail.html', context={
        'tournament': tournament
    })

@login_required
def tournament_admin(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    staffAccount = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staffAccount is None or not staffAccount.role.can_delete:
        return HttpResponse('Not authorized', 401)

    return render(request, 'tournament/tournament_admin.html', context={
        'tournament': tournament
    })

@login_required
def delete_tournament(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    staffAccount = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staffAccount is None or not staffAccount.role.can_delete:
        return HttpResponse('Not authorized', 401)
    
    tournament.delete()

    return HttpResponseRedirect(reverse('cardDatabase-tournament-list'))