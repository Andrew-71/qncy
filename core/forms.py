from django import forms
from django.contrib.auth.forms import UserCreationForm

from core.models import User

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "pfp"]

# UserChangeForm includes things we might not want
class SettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "pfp"]
