import datetime
from django.db import models
from django.db.models import Sum, Case, When, IntegerField
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import PermissionDenied

# User: email, username, pass, profile pic, registration date, rating
class User(AbstractUser):
    pfp = models.ImageField(upload_to="profile/", blank=True)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        q_score = QuestionVote.objects.filter(question__author=self).aggregate(
            score=Sum(
                Case(
                    When(up=True, then=1),
                    When(up=False, then=-1),
                    output_field=IntegerField(),
                )
            )
        )["score"] or 0
        a_score = AnswerVote.objects.filter(answer__author=self).aggregate(
            score=Sum(
                Case(
                    When(up=True, then=1),
                    When(up=False, then=-1),
                    output_field=IntegerField(),
                )
            )
        )["score"] or 0
        self.rating = q_score + a_score
        self.save()

# Tag: ...tag
class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

# Question: title, content, author, creation date, tags, rating
class Question(models.Model):
    # StackOverflow appears to have this as limit via
    # https://meta.stackexchange.com/questions/176445/
    title = models.CharField(max_length=150)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="questions")
    created_at = models.DateTimeField(default=datetime.datetime.now)
    tags = models.ManyToManyField(Tag, blank=True)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        self.rating = self.question_vote.aggregate(
            score=Sum(
                Case(
                    When(up=True, then=1),
                    When(up=False, then=-1),
                    output_field=IntegerField(),
                )
            )
        )["score"] or 0
        self.save()
    
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
            self.author.update_rating()
            return
        elif existing and not vote.up and not up:
            vote.delete()
            self.update_rating()
            self.author.update_rating()
            return
        vote.up = up
        vote.save()
        self.update_rating()
        self.author.update_rating()
        return

    def __str__(self):
        return self.title

# Answer: content, author, creation date, accepted flag, rating
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="question_answer")
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    accepted = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        self.rating = self.answer_vote.aggregate(
            score=Sum(
                Case(
                    When(up=True, then=1),
                    When(up=False, then=-1),
                    output_field=IntegerField(),
                )
            )
        )["score"] or 0
        self.save()

    def accept(self, user: User):
        if user != self.question.author:
            raise PermissionDenied()
        answer_accepted = Answer.objects.filter(question=self.question,accepted=True)
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
            self.author.update_rating()
            return
        elif existing and not vote.up and not up:
            vote.delete()
            self.update_rating()
            self.author.update_rating()
            return
        vote.up = up
        vote.save()
        self.update_rating()
        self.author.update_rating()
        return
    
    def __str__(self):
        return self.author.username + " - " + self.question.title

class QuestionVote(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="question_vote")
                       
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
        related_name="question_vote")
    up = models.BooleanField(blank=False, default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'question'], name="unique_question_vote"),
        ]
    
    def __str__(self):
        return f"{'UP' if self.up else 'DOWN'} - {self.user.username} - {self.question.title}"

class AnswerVote(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="answer_vote")
                       
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
        related_name="answer_vote")
    up = models.BooleanField(blank=False, default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'answer'], name="unique_answer_vote"),
        ]
    
    def __str__(self):
        return f"{'UP' if self.up else 'DOWN'} - {self.user.username} - {self.answer.content[:20]}"
