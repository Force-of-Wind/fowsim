from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST


from cardDatabase.models.Tournament import Tournament, TournamentStaff, StaffRole

from cardDatabase.models import Profile

@login_required
@require_POST
def post (request, tournament_id):
    tournament = get_object_or_404(Tournament, pk=tournament_id)

    staff_account = TournamentStaff.objects.filter(tournament = tournament, profile = request.user.profile).first()
    
    if staff_account is None or not staff_account.role.can_delete:
        return JsonResponse({'error': 'Not authorized'}, status=401)
    
    print(request)
    print(request.POST)

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
