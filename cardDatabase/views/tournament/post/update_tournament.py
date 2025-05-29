from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST

from ....models.Tournament import Tournament, TournamentLevel, TournamentStaff
from ....models.Banlist import Format
from .. import tournament_constants as TOURNAMENTCONS

from ..utils.utilities import check_value_is_meta_data, map_meta_data, any_empty

@login_required
@require_POST
def post(request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    staff_account = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staff_account is None or not staff_account.role.can_write:
        return HttpResponse('Not authorized', 401)
        
    
    if not request.method == "POST":
        raise Http404
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
        return HttpResponseRedirect(reverse('cardDatabase-error-edit-tournament',  kwargs={'tournament_id': tournament_id}))

    tournament.title=title
    tournament.is_online = is_online
    tournament.format = Format.objects.get(pk=format_id)
    tournament.level = TournamentLevel.objects.get(pk=level_id)
    tournament.start_datetime = start_date_time
    tournament.registration_deadline = registration_deadline
    tournament.deck_edit_deadline = deck_edit_deadline
    tournament.meta_data = meta_data
    tournament.save()

    return HttpResponseRedirect(reverse('cardDatabase-admin-tournament', kwargs={'tournament_id': tournament.id}))