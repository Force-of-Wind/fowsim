from django.contrib.auth.decorators import login_required

from fowsim.decorators import site_admins


@login_required
@site_admins
def get(request):
    return 1 / 0