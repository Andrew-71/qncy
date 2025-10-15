from django.urls import path

from . import views

from django.contrib.auth import views as auth_views

app_name = "qncy"
urlpatterns = [
    path("", views.index, name="index"),
    path("question/<int:question_id>/", views.question, name="question"),
    path("tagged/<str:tag_name>/", views.tag, name="tagged"),

    path("logout", views.logout_view, name="logout"),

    path("login", auth_views.LoginView.as_view()),
]
