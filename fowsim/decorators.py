import json

from functools import wraps

from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from django.conf import settings
from fowsim.enums import TournamentPermissions

from cardDatabase.models.Tournament import Tournament, TournamentStaff


def site_admins(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_active and request.user.profile.site_admin:
            return function(request, *args, **kwargs)
        else:
            return redirect('/')
    return wrap


def desktop_only(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user_agent.is_mobile or request.user_agent.is_tablet:
            return redirect(reverse('cardDatabase-desktop-only'))
        else:
            return function(request, *args, **kwargs)
    return wrap


def logged_out(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('cardDatabase-user-decklists'))
        else:
            return function(request, *args, **kwargs)
    return wrap


def mobile_only(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user_agent.is_mobile or request.user_agent.is_tablet:
            return function(request, *args, **kwargs)
        else:
            return redirect(reverse('cardDatabase-mobile-only'))
    return wrap


def reddit_bot(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.method == 'POST':
            try:
                data = json.loads(request.body.decode('UTF-8'))
            except (json.JSONDecodeError, json.decoder.JSONDecodeError):
                return HttpResponse('Invalid json', status=401)
            if data.get('api_key', None) == settings.REDDIT_BOT_API_KEY:
                return function(request, *args, **kwargs)
        return HttpResponse('Invalid api key', status=401)
    return wrap

def check_tournament_staff_permissions(permission):
    def decorator(function):
        def wrap(request, *args, **kwargs):
            tournament_id = (
                request.GET.get('tournament_id') or
                request.POST.get('tournament_id') or
                kwargs.get('tournament_id')
            )

            if not tournament_id:
                return HttpResponse('Bad Request', status=400)
            
            if not request.user.is_authenticated:
                return HttpResponse('User not authenticated.', status=403)

            try:
                tournament = Tournament.objects.get(pk=tournament_id)
            except Tournament.DoesNotExist:
                return HttpResponse('Tournament not found', status=404)

            staff_account = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
        
            if staff_account is None:
                return HttpResponse('Not authorized', 401)
            
            if(permission == TournamentPermissions.CAN_READ and not staff_account.role.can_read):
                return HttpResponse('Not authorized', 401)
            
            if(permission == TournamentPermissions.CAN_WRITE and not staff_account.role.can_write):
                return HttpResponse('Not authorized', 401)
            
            if(permission == TournamentPermissions.CAN_DELETE and not staff_account.role.can_delete):
                return HttpResponse('Not authorized', 401)

            request.tournament = tournament  # Attach for use in view

            request.staff_account = staff_account  # Attach for use in view

            return function(request, *args, **kwargs)

        return wrap
    return decorator

def tournament_owner(function):
    return check_tournament_staff_permissions(TournamentPermissions.CAN_DELETE)(function)

def tournament_admin(function):
    return check_tournament_staff_permissions(TournamentPermissions.CAN_WRITE)(function)

def tournament_reader(function):
    return check_tournament_staff_permissions(TournamentPermissions.CAN_READ)(function)