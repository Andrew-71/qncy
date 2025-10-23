from django.urls import path

from . import views

app_name = "qncy"
urlpatterns = [
    path("", views.index, name="index"),
    path("ask", views.ask, name="ask"),
    path("question/<int:question_id>/", views.question, name="question"),
    path("tagged/<tag_name>/", views.tag, name="tagged"),

    path("vote/q/<int:question_id>/", views.vote_question, name="vote_question"),
    path("vote/a/<int:answer_id>/", views.vote_answer, name="vote_answer"),
]
