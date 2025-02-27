import json

from functools import wraps

from django.http import HttpResponse
from django.shortcuts import redirect, reverse
from django.conf import settings


def site_admins(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        print(request.user.profile.site_admin)
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
