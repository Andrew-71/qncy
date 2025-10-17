import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser

# TODO User: email, username, pass, profile pic, registration date, rating
class User(AbstractUser):
    pfp = models.ImageField(upload_to="profile/", blank=True)

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
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    tags = models.ManyToManyField(Tag, blank=True)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.title

# Answer: content, author, creation date, accepted flag, rating
class Answer(models.Model):
    # NOTE: PROTECT may be better here:
    # you might still want to see your answer to a deleted question
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=datetime.datetime.now)
    accepted = models.BooleanField(default=False)
    rating = models.IntegerField(default=0)
    
    def __str__(self):
        return self.author.username + " - " + self.question.title
