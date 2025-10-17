from django import forms
from django.contrib.auth.forms import UserCreationForm

from qncy.models import Question, User

class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "pfp"]

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["title", "content", "tags"]
