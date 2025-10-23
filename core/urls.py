from django.urls import path

from . import views

from django.contrib.auth import views as auth_views

app_name = "core"
urlpatterns = [
    path("register", views.register, name="register"),
    path("settings", views.settings, name="settings"),
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
    path("login", auth_views.LoginView.as_view(), name="login"),
]
