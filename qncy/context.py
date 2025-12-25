from django.core.cache import cache

from qncy.models import Tag
from core.models import User


# Retrieve top tags and users from cache
def common_context(request):
    top_tags = cache.get("top_tags", Tag.objects.get_top())
    top_users = cache.get("top_users", User.objects.get_top())

    return {"common": {"top_tags": top_tags, "top_users": top_users}}
