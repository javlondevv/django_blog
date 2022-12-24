from apps.models import Post, Category, Info
from root import settings


def custom_posts(request):
    return {
        "custom_posts": Post.objects.order_by('-created_at')
    }


def custom_categories(request):
    return {
        "custom_categories": Category.objects.all()
    }


def site_info(request):
    return {
        "info": Info.objects.first()
    }
