from django.urls import path

from core.views import register, settings, logout_view

from django.contrib.auth import views as auth_views

app_name = "core"
urlpatterns = [
    path("register", register, name="register"),
    path("settings", settings, name="settings"),
    path("logout", logout_view, name="logout"),
    path("login", auth_views.LoginView.as_view(), name="login"),
]
