from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from qncy.models import Question, User, Answer

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "pfp"]

# UserChangeForm includes things we might not want
class SettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "pfp"]

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ["title", "content", "tags"]

class AnswerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AnswerForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs['placeholder'] = 'Enter your answer here.'

    class Meta:
        model = Answer
        fields = ["content"]
        labels = {
            "content": "Your answer",
        }
