from apps.models import Post, Category


def custom_posts(request):
    return {
        "custom_posts": Post.objects.order_by('-created_at')
    }

def custom_categories(request):
    return {
        "custom_categories": Category.objects.all()
    }
