from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Sum, Case, When, IntegerField, Count, OuterRef, Subquery, F
from django.db.models.functions import Coalesce
from datetime import timedelta

from qncy.models import Tag, QuestionVote, AnswerVote
from core.models import User


class Command(BaseCommand):
    help = "Generates sidebar data"

    def handle(self, *args, **options):
        self.stdout.write("Generating sidebar data...")
        week_ago = timezone.now() - timedelta(days=7)
        three_weeks_ago = timezone.now() - timedelta(days=21)

        top_tags = (
            Tag.objects.filter(question__created_at__gte=three_weeks_ago)
            .annotate(q_count=Count("question"))
            .order_by("-q_count", "name")[:10]
        )

        score_logic = Sum(
            Case(
                When(up=True, then=1),
                When(up=False, then=-1),
                output_field=IntegerField(),
            )
        )

        q_votes_sq = (
            QuestionVote.objects.filter(
                question__author=OuterRef("pk"), created_at__gte=week_ago
            )
            .values("question__author")
            .annotate(total=score_logic)
            .values("total")
        )

        a_votes_sq = (
            AnswerVote.objects.filter(
                answer__author=OuterRef("pk"), created_at__gte=week_ago
            )
            .values("answer__author")
            .annotate(total=score_logic)
            .values("total")
        )

        top_users = (
            User.objects.annotate(
                weekly_q_score=Coalesce(Subquery(q_votes_sq), 0),
                weekly_a_score=Coalesce(Subquery(a_votes_sq), 0),
            )
            .annotate(weekly_total=F("weekly_q_score") + F("weekly_a_score"))
            .filter(weekly_total__gte=0)  # hide users with negative score...
            .order_by("-weekly_total")[:10]
        )

        # cache for 7 days
        cache.set("top_users", list(top_users), 60 * 60 * 24 * 7)
        cache.set("top_tags", list(top_tags), 60 * 60 * 24 * 7)

        self.stdout.write(self.style.SUCCESS("Sidebar data cached successfully"))
