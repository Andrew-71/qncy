from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect

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


@require_POST
def logout_view(request):
    logout(request)
    next = request.POST.get("next", "/")
    return HttpResponseRedirect(next)
