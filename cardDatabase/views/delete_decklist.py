from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from cardDatabase.models import DeckList


@csrf_exempt
@login_required
def get(request, decklist_id=None):
    if decklist_id:
        try:
            decklist = DeckList.objects.get(pk=decklist_id)
            if decklist.profile.user == request.user:  # Check they aren't deleting other people's lists
                decklist.delete()
        except DeckList.DoesNotExist:
            pass
    return HttpResponseRedirect(reverse('cardDatabase-user-decklists'))