from django.db import models
from django.db.models import Sum, Case, When, IntegerField, Count

from core.models import User


# Tag: ...tag
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=False)

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("author")
            .annotate(answer_count=Count("question_answer"))
            .prefetch_related("tags")
        )

    def get_new(self):
        return self.order_by("-created_at")

    def get_hot(self):
        # NOTE: Right now this is more of a "top". Add time cut-off?
        return self.order_by("-rating", "-created_at")

    def get_tagged(self, tag):
        return self.filter(tags=tag).order_by("-created_at")


# Question: title, content, author, creation date, tags, rating
class Question(models.Model):
    objects = QuestionManager()

    # StackOverflow appears to have these as limits via
    # https://meta.stackexchange.com/questions/176445/
    title = models.CharField(max_length=150)
    content = models.TextField(max_length=30000)
    author = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="questions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, blank=True)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        self.rating = (
            self.question_vote.aggregate(
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
        self.author.update_rating()
        self.save(update_fields=["rating"])

    def answers(self):
        return self.question_answer.all().count()

    def vote(self, user: User, up: bool):
        vote_old = QuestionVote.objects.filter(question=self, user=user)
        vote = QuestionVote(user=user, question=self)
        existing = False
        if vote_old.exists():
            vote = vote_old.get()
            existing = True
        if existing and vote.up and up:
            vote.delete()
            self.update_rating()
            return
        elif existing and not vote.up and not up:
            vote.delete()
            self.update_rating()
            return
        vote.up = up
        vote.save()
        self.update_rating()
        return

    def __str__(self):
        return self.title


class AnswerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("author")

    def for_question(self, question):
        return self.filter(question=question).order_by("-accepted", "-rating")


# Answer: content, author, creation date, accepted flag, rating
class Answer(models.Model):
    objects = AnswerManager()

    question = models.ForeignKey(
        "qncy.Question", on_delete=models.CASCADE, related_name="question_answer"
    )
    content = models.TextField(max_length=30000)
    author = models.ForeignKey("core.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        self.rating = (
            self.answer_vote.aggregate(
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
        self.author.update_rating()
        self.save(update_fields=["rating"])

    def accept(self):
        answer_accepted = Answer.objects.filter(question=self.question, accepted=True)
        if answer_accepted.exists():
            answer_accepted = answer_accepted.get()
            answer_accepted.accepted = False
            answer_accepted.save()
            if answer_accepted == self:
                return
        self.accepted = True
        self.save()

    def vote(self, user: User, up: bool):
        vote_old = AnswerVote.objects.filter(answer=self, user=user)
        vote = AnswerVote(user=user, answer=self)
        existing = False
        if vote_old.exists():
            vote = vote_old.get()
            existing = True
        if existing and vote.up and up:
            vote.delete()
            self.update_rating()
            return
        elif existing and not vote.up and not up:
            vote.delete()
            self.update_rating()
            return
        vote.up = up
        vote.save()
        self.update_rating()
        return

    def __str__(self):
        return self.author.username + " - " + self.question.title


class QuestionVote(models.Model):
    question = models.ForeignKey(
        "qncy.Question", on_delete=models.CASCADE, related_name="question_vote"
    )

    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="question_vote"
    )
    up = models.BooleanField(blank=False, default=True, verbose_name="voted up")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "question"], name="unique_question_vote"
            ),
        ]

    def __str__(self):
        return f"{'UP' if self.up else 'DOWN'} - {self.user.username} - {self.question.title}"


class AnswerVote(models.Model):
    answer = models.ForeignKey(
        "qncy.Answer", on_delete=models.CASCADE, related_name="answer_vote"
    )

    user = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="answer_vote"
    )
    up = models.BooleanField(blank=False, default=True, verbose_name="voted up")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "answer"], name="unique_answer_vote"
            ),
        ]

    def __str__(self):
        return f"{'UP' if self.up else 'DOWN'} - {self.user.username} - {self.answer.content[:20]}"
