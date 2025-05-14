from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST


from .....models.Tournament import Tournament, TournamentStaff


@login_required
@require_POST
def post(request, tournament_id):
    updated_state = request.POST.get('status')
    tournament = get_object_or_404(Tournament, pk=tournament_id)
    staff_account = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staff_account is None or not staff_account.role.can_delete:
        return JsonResponse({'error': 'Not authorized'}, status=401)
    
    if updated_state is None:
        return JsonResponse({'error': 'Payload incorrect'}, status=400)
    
    tournament.phase = updated_state
    tournament.save()

    return JsonResponse({}, status=200)