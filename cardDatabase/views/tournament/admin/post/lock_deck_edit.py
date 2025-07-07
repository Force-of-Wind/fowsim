from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from cardDatabase.models.Tournament import TournamentPlayer

from fowsim import constants as CONS
from fowsim.decorators import tournament_admin

@login_required
@require_POST
@tournament_admin
def post (request, tournament_id):
    tournament = request.tournament
    
    data = dict(request.POST)
    
    lock_state = 'lockState' in data
    
    if tournament.deck_edit_locked != lock_state:
        tournament.deck_edit_locked = lock_state
        #update the lock state on each deck
        tournament.save()
        
        for player in TournamentPlayer.objects.filter(tournament=tournament):
            if lock_state:
                player.deck.deck_lock = CONS.MODE_TOURNAMENT
            else:
                player.deck.deck_lock = ''

            player.deck.save()
        

    return JsonResponse({'success': True})