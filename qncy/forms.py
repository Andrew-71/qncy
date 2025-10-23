from django import forms

from qncy.models import Question, Answer

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
