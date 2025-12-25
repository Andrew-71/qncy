import os
from uuid import uuid4
from datetime import timedelta

from django.db import models
from django.db.models import Sum, Case, When, IntegerField, OuterRef, Subquery, F
from django.contrib.auth.models import AbstractUser, UserManager
from django.apps import apps
from django.utils.deconstruct import deconstructible
from django.utils import timezone
from django.db.models.functions import Coalesce


# Set file
@deconstructible
class ImagePath(object):
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split(".")[-1]
        filename = "{}.{}".format(uuid4().hex, ext)
        return os.path.join(self.path, filename)


profile_image_path = ImagePath("profile/")


class CustomUserManager(UserManager):
    def get_top(self):
        week_ago = timezone.now() - timedelta(days=7)
        QuestionVote = apps.get_model("qncy.QuestionVote")
        AnswerVote = apps.get_model("qncy.AnswerVote")

        score_logic = Sum(
            Case(
                When(up=True, then=1),
                When(up=False, then=-1),
                output_field=IntegerField(),
            )
        )

        q_votes_sq = (
            QuestionVote.objects.filter(
                question__author=OuterRef("pk"), created_at__gte=week_ago
            )
            .values("question__author")
            .annotate(total=score_logic)
            .values("total")
        )

        a_votes_sq = (
            AnswerVote.objects.filter(
                answer__author=OuterRef("pk"), created_at__gte=week_ago
            )
            .values("answer__author")
            .annotate(total=score_logic)
            .values("total")
        )

        return (
            self.annotate(
                weekly_q_score=Coalesce(Subquery(q_votes_sq), 0),
                weekly_a_score=Coalesce(Subquery(a_votes_sq), 0),
            )
            .annotate(weekly_total=F("weekly_q_score") + F("weekly_a_score"))
            .filter(weekly_total__gte=0)  # hide users with negative score...
            .order_by("-weekly_total")[:10]
        )


# User: email, username, pass, profile pic, registration date, rating
class User(AbstractUser):
    objects = CustomUserManager()

    pfp = models.ImageField(
        upload_to=profile_image_path, verbose_name="Profile image", blank=True
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
        self.save(update_fields=["rating"])
