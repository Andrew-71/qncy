from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import ClearableFileInput

from core.models import User


class ImageFieldWidget(ClearableFileInput):
    template_name = "widgets/image_with_preview.html"


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "pfp"]


# UserChangeForm includes things we might not want
class SettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "pfp"]
        widgets = {
            "pfp": ImageFieldWidget,
        }
