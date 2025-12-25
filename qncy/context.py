from django.core.cache import cache


# Retrieve top tags and users from cache
def common_context(request):
    top_tags = cache.get("top_tags", [])
    top_users = cache.get("top_users", [])

    return {"common": {"top_tags": top_tags, "top_users": top_users}}
