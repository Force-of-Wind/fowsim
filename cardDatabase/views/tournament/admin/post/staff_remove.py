from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from cardDatabase.models.Tournament import TournamentStaff

from fowsim.decorators import tournament_owner

@login_required
@require_POST
@tournament_owner
def post (request, tournament_id):
    tournament = request.tournament

    key = request.POST.get('key')

    existing_staff = TournamentStaff.objects.filter(tournament=tournament, pk=key).first()

    if existing_staff is None:
        return JsonResponse({'error': 'Staff not found!'}, status=400)
    
    existing_staff.delete()

    return JsonResponse({ 'success': True })
