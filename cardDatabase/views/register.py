from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.urls import reverse

from cardDatabase.forms import UserRegistrationForm
from fowsim.decorators import logged_out


@logged_out
def get(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect(reverse('cardDatabase-user-decklists'))
    else:
        form = UserRegistrationForm()
    return render(request, 'cardDatabase/html/register.html', {'form': form})