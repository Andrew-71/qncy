from django import forms

from qncy.models import Question, Answer, Tag
from django.core.exceptions import ValidationError


def validate_tag_list(value):
    values = value.split(",")
    if len(values) > 5:
        raise ValidationError("You cannot apply more than 5 tags")
    for val in values:
        if len(val.strip()) == 0:
            raise ValidationError("Some items on the list have length of zero.")


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            "title",
            "content",
        ]

    tags = forms.CharField(
        required=False,
        validators=[validate_tag_list],
        help_text="Input comma-separated tags.",
        label="tags",
    )

    def save(self, commit=True):
        question: Question = super(QuestionForm, self).save(commit=False)

        # This looks rather ugly, but we seemingly can't add objects to
        # question.tags until we save it, so as far as I can tell this is
        # what we're left with.
        if commit:
            question.save()
            tag_names = list(
                map(lambda x: x.strip(), self.cleaned_data["tags"].split(","))
            )
            # existing = Tag.objects.filter(name__in=tag_names)
            # ^ this looks nice, but it's easier for us to iterate since we
            #   restrict to 5 tags (like on StackOverflow) anyway
            for tag in tag_names:
                if len(tag) == 0:  # avoid creating empty tags
                    continue
                tag_obj = Tag.objects.filter(name=tag)
                if tag_obj.exists():
                    question.tags.add(tag_obj.get())
                else:
                    new_tag = Tag.objects.create(name=tag)
                    question.tags.add(new_tag)
            question.save()
        return question


class AnswerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AnswerForm, self).__init__(*args, **kwargs)
        self.fields["content"].widget.attrs["placeholder"] = "Enter your answer here."

    class Meta:
        model = Answer
        fields = ["content"]
        labels = {
            "content": "Your answer",
        }
