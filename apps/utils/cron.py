import os

import django
from django.db.models import Q

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "root.settings")
django.setup()

from apps.models import Post
import datetime


def cron_job():
    date = datetime.date.today()
    date_delta = datetime.timedelta(7)
    # Post.objects.filter(Q(created_at__lt=date - date_delta), Q(status=Post.Status.CANCEL)).delete()
    s = Post.objects.get(pk=2)
    s.title = 'ssss'
    s.save()