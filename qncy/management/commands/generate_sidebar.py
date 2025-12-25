from django.core.management.base import BaseCommand
from django.core.cache import cache

from qncy.models import Tag
from core.models import User


class Command(BaseCommand):
    help = "Generates sidebar data"

    def handle(self, *args, **options):
        self.stdout.write("Generating sidebar data...")
        top_users = User.objects.get_top()
        top_tags = Tag.objects.get_top()

        # cache for 7 days
        cache.set("top_users", list(top_users), 60 * 60 * 24 * 7)
        cache.set("top_tags", list(top_tags), 60 * 60 * 24 * 7)

        self.stdout.write(self.style.SUCCESS("Sidebar data cached successfully"))
