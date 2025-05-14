from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST

from ....models.Tournament import Tournament, TournamentLevel, TournamentStaff, StaffRole
from ....models.Banlist import Format
from ..utils.utilities import check_value_is_meta_data, map_meta_data, any_empty
from .. import tournament_constants as TOURNAMENTCONS

@login_required
@require_POST
def post(request):
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