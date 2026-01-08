from django.contrib.auth import logout as django_logout
from django.http import HttpResponseRedirect
from django.urls import reverse


def get(request):
    django_logout(request)
    return HttpResponseRedirect(reverse("cardDatabase-search"))
