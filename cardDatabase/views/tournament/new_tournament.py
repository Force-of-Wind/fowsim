import json
import re
import datetime

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ...models.Tournament import TournamentLevel
from ...models.Banlist import Format
from . import tournament_constants as TOURNAMENTCONS

@login_required
def get(request, error = False):
    return render(request, 'tournament/tournament_create.html', context={
        'meta_data': TOURNAMENTCONS.TOURNAMENT_DEFAULT_META_DATA,
        'formats': Format.objects.all().order_by('pk'),
        'levels': TournamentLevel.objects.all(),
        'error': error
    })