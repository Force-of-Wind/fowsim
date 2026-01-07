from django.shortcuts import render


def get(request):
    return render(request, "cardDatabase/html/mobile_only.html", {})
