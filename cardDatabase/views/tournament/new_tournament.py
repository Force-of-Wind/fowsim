import json
import re
import datetime

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse

from cardDatabase.models.Tournament import TournamentLevel
from cardDatabase.models.Banlist import Format
from . import tournament_constants as TOURNAMENTCONS

@login_required
def get(request, error = False):
    if not request.user.profile.can_create_tournament:
        return HttpResponseRedirect(reverse('cardDatabase-tournament-create-unauthorized'))

    return render(request, 'tournament/tournament_create.html', context={
        'meta_data': TOURNAMENTCONS.TOURNAMENT_DEFAULT_META_DATA,
        'formats': Format.objects.all().order_by('pk'),
        'levels': TournamentLevel.objects.all(),
        'error': error
    })