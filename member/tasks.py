from celery import shared_task
from . import models
from rest_framework.response import Response
from django.db.models import F
from django.db import transaction

@shared_task
def vote(user, data):
    user_object = models.UserInfo.objects.get(username=user.get('username'))
    if user_object.voted:
        return '已投票'
    queryset = models.UserInfo.objects.get(username=data.get('candidate'))

    while True:
        before_data = queryset.vote  # 更新前的數字
        update_data = models.UserInfo.objects.filter(username=data.get('candidate'), vote=before_data)
        if update_data:
            update_data.update(vote=before_data+1)
            break

    # queryset.vote = F('vote') + 1
    # queryset.save()
    user_object.voted = True
    user_object.save()
    return {"status": True}


@shared_task
def add(x, y):
    return x+y