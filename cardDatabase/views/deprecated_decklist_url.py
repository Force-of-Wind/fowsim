from django.shortcuts import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect


@login_required
def get(request):
    return HttpResponseRedirect(reverse("cardDatabase-view-users-decklist", kwargs={"username": request.user.username}))
