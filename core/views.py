from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from core.models import User
from core.forms import RegisterForm, SettingsForm


def register(request):
    user = User()
    form = RegisterForm(request.POST or None, request.FILES or None, instance=user)
    if form.is_valid():
        form.save()
        login(request, user)
        return redirect("qncy:index")
    return render(request, "registration/register.html", {"form": form})


@login_required
def settings(request):
    form = SettingsForm(
        request.POST or None, request.FILES or None, instance=request.user
    )
    if form.is_valid():
        form.save()
        return redirect("qncy:index")
    return render(request, "registration/settings.html", {"form": form})
