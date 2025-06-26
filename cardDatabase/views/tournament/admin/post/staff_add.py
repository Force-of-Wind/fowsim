from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from cardDatabase.models.Tournament import TournamentStaff, StaffRole

from cardDatabase.models import Profile

from fowsim.decorators import tournament_owner

@login_required
@require_POST
@tournament_owner
def post (request, tournament_id):
    tournament = request.tournament

    username = request.POST.get('userName')
    role = request.POST.get('role')

    if username is None:
        return JsonResponse({'error': 'UserName cannot be empty!'}, status=400)
    
    if role is None:
        return JsonResponse({'error': 'Role cannot be empty!'}, status=400)
    
    staff_user = Profile.objects.filter(user__username=username).first()

    existing_staff = TournamentStaff.objects.filter(tournament=tournament, profile = staff_user).first()

    if existing_staff is not None:
        return JsonResponse({'error': 'User already is Staff!'}, status=400)

    if staff_user is None:
        return JsonResponse({'error': 'User with name not found!'}, status=400)
    
    staff_role = StaffRole.objects.filter(pk=role).first()

    if staff_role is None:
         return JsonResponse({'error': 'Role not found!'}, status=400)
    
    TournamentStaff.objects.create(tournament=tournament, profile=staff_user, role=staff_role)

    return JsonResponse({ 'success': True })
