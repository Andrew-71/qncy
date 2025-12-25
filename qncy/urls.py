from django.urls import path

from . import views
from . import centrifugo

app_name = "qncy"
urlpatterns = [
    path("", views.index, name="index"),
    path("hot", views.hot, name="hot"),
    path("ask", views.ask, name="ask"),
    path("user/<user_name>/", views.by_user, name="user_profile"),
    path("question/<int:question_id>/", views.question, name="question"),
    path("question/<int:question_id>/answers/", views.answers, name="question_answers"),
    path("tagged/<tag_name>/", views.tagged, name="tagged"),
    path("vote/q/<int:question_id>/", views.vote_question, name="vote_question"),
    path("vote/a/<int:answer_id>/", views.vote_answer, name="vote_answer"),
    path("accept/a/<int:answer_id>/", views.accept_answer, name="accept_answer"),
    path("search/", views.search, name="search"),
    path("centrifugo/connect/", centrifugo.connect, name="connect"),
    path("centrifugo/subscribe/", centrifugo.subscribe, name="subscribe"),
    path("centrifugo/publish/", centrifugo.publish, name="publish"),
]
