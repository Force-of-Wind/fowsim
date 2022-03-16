from functools import wraps

from django.http import HttpResponseRedirect
from django.shortcuts import redirect, reverse
from django.conf import settings


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
            return redirect(reverse('cardDatabase-mobile-only'))
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
