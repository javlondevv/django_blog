from datetime import date
from django.db.models import Count
from apps.models import Category, Post, PostViewHistory, AboutUs, Info


def context_category(request):
    return {
        'categories': Category.objects.annotate(p_count=Count('post')).order_by('-p_count'),
        'tags': Category.objects.annotate(p_count=Count('post')).order_by('-p_count')
    }


def context_info(request):
    return {
        'info': Info.objects.first()
    }


def context_post(request):
    trending_post = PostViewHistory.objects.filter(viewed_at__month__gt=date.today().month - 1)
    trending_post = trending_post.values_list('post', flat=True).annotate(count=Count('viewed_at')).order_by('-count')[
                    :5]
    return {
        'posts': Post.objects.all(),
        'feature_posts': Post.objects.order_by('-created_at')[:3],
        'trending_post': Post.objects.filter(id__in=list(trending_post)).order_by('-views')
        # 'trending_post': PostViewHistory.objects.filter(viewed_at__month__gt=date.today().month - 1)
    }
