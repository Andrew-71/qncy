import os
from uuid import uuid4
from django.db import models
from django.db.models import Sum, Case, When, IntegerField
from django.contrib.auth.models import AbstractUser

from django.apps import apps

from django.utils.deconstruct import deconstructible


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


# User: email, username, pass, profile pic, registration date, rating
class User(AbstractUser):
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
