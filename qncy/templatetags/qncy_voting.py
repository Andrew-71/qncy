from django import template

from qncy.models import Question, Answer

register = template.Library()


@register.inclusion_tag("qncy/voting.html")
def vote(submission: Question | Answer, user):
    # This unfortunately increases SQL Queries by a bit.
    # I don't know how to remove this for now...
    exists = False
    up = False
    if user.is_authenticated:
        vote = submission.votes.filter(user=user)
        up = True
        if vote.exists():
            exists = True
            up = vote.get().up
    return {
        "exists": exists,
        "up": up,
        "submission": submission,
    }
