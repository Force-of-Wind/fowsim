from functools import wraps

from django.http import HttpResponseRedirect
from django.shortcuts import redirect


def site_admins(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_active and request.user.profile.site_admin:
            return function(request, *args, **kwargs)
        else:
            return redirect('/')
    return wrap
