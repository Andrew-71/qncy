from django.db import models
from django.db.models import Sum, Case, When, IntegerField
from django.contrib.auth.models import AbstractUser

from django.apps import apps


# User: email, username, pass, profile pic, registration date, rating
class User(AbstractUser):
    pfp = models.ImageField(
        upload_to="profile/", verbose_name="Profile image", blank=True
    )
    rating = models.IntegerField(default=0)

    def update_rating(self):
        QuestionVote = apps.get_model("qncy.QuestionVote")
        q_score = (
            QuestionVote.objects.filter(question__author=self).aggregate(
                score=Sum(
                    Case(
                        When(up=True, then=1),
                        When(up=False, then=-1),
                        output_field=IntegerField(),
                    )
                )
            )["score"]
            or 0
        )
        AnswerVote = apps.get_model("qncy.AnswerVote")
        a_score = (
            AnswerVote.objects.filter(answer__author=self).aggregate(
                score=Sum(
                    Case(
                        When(up=True, then=1),
                        When(up=False, then=-1),
                        output_field=IntegerField(),
                    )
                )
            )["score"]
            or 0
        )
        self.rating = q_score + a_score
        self.save()
