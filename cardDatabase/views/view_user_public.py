from django.shortcuts import render
from django.http import Http404

from cardDatabase.models import DeckList, Format
from django.contrib.auth.models import User


def get(request, username=None):
    if username is not None:
        ctx = dict()
        try:
            if request.user.username == username:
                #  Dont filter by is_public
                ctx["decklists"] = DeckList.objects.filter(profile=request.user.profile).order_by("-last_modified")
                ctx["is_owner"] = True
            else:
                ctx["decklists"] = DeckList.objects.filter(
                    profile=User.objects.get(username=username).profile, public=True
                ).order_by("-last_modified")
                ctx["is_owner"] = False
        except User.DoesNotExist:
            raise Http404

        ctx["formats"] = Format.objects.all()

        return render(request, "cardDatabase/html/user_decklists.html", context=ctx)
    else:
        raise Http404
