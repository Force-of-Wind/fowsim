from django.shortcuts import render


def get(request):
    return render(request, 'cardDatabase/html/desktop_only.html', {})