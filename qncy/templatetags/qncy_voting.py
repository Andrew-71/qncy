from django import template

from qncy.models import Question, Answer

register = template.Library()


@register.inclusion_tag("qncy/voting.html")
def vote(submission: Question | Answer, user):
    exists = False
    up = False
    if hasattr(submission, "user_voted") and hasattr(submission, "user_vote_up"):
        exists = bool(getattr(submission, "user_voted"))
        up = bool(getattr(submission, "user_vote_up", True))
    return {
        "exists": exists,
        "up": up,
        "submission": submission,
    }
