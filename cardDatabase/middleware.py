def show_debug_toolbar(request):
    return request.user.is_superuser and request.user.profile.see_debug_toolbar
