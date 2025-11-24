from django import template

from qncy.models import Question, Answer

register = template.Library()


@register.inclusion_tag("qncy/voting.html")
def vote(submission: Question | Answer, user):
    # This unfortunately increases SQL Queries by a bit.
    # I don't know how to remove this for now...
    vote = submission.votes.filter(user=user)
    up = True
    if vote.exists():
        up = vote.get().up
    return {
        "exists": vote.exists(),
        "up": up,
        "submission": submission,
    }
