from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from fowsim.decorators import tournament_reader

@login_required
@tournament_reader
def get(request, tournament_id):
    tournament = request.tournament
    
    players = map_tournament_player(tournament.players.order_by('standing').all())

    return JsonResponse(players, safe=False)

@login_required
@tournament_reader
def getHtml(request, tournament_id):
    tournament = request.tournament
    staff_account = request.staff_account
    
    players = map_tournament_player(tournament.players.order_by('standing').all())

    return render(request, 'tournament/admin/player_renderer.html', context={
        'tournament': tournament,
        'players':players,
        'staff': staff_account.role
    })

def map_tournament_player(players):
    mappedPlayers = []

    for player in players:
        first_name = ''
        last_name = ''

        additional_info_fields = []

        for field in player.user_data:
            if field['name'] == 'firstname':
                first_name = field['value']
            elif field['name'] == 'lastname':
                last_name = field['value']
            else:
                additional_info_fields.append(field)

        ruler_names = []
        if not player.deck.get_deck_rulers:
            continue
        rulers = player.deck.get_deck_rulers.order_by('card__name')
        for ruler in rulers:
            ruler_names.append(ruler.card.name)
        ruler_combo_name = ' + '.join(ruler_names)
            

        playerObj = {
            "id": player.pk,
            "firstname": first_name,
            "lastname": last_name,
            "additionalInfoFields": additional_info_fields,
            "dropped": player.dropped_out,
            "notes": player.notes,
            "standing": player.standing,
            "status": player.registration_status,
            "username": player.profile.user.username,
            "decklistId": player.deck.pk,
            "decklistShareCode": player.deck.shareCode,
            "ruler": ruler_combo_name
        }
        mappedPlayers.append(playerObj)
        
    return mappedPlayers