from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST


from cardDatabase.models.Tournament import Tournament, TournamentStaff

@login_required
@require_POST
def post (request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    staff_account = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staff_account is None or not staff_account.role.can_delete:
        return JsonResponse({'error': 'Not authorized'}, status=401)
    
    key = request.POST.get('key')

    existing_staff = TournamentStaff.objects.filter(tournament=tournament, pk=key).first()

    if existing_staff is None:
        return JsonResponse({'error': 'Staff not found!'}, status=400)
    
    existing_staff.delete()

    return JsonResponse({ 'success': True })
