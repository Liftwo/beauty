import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE',  'beauty.settings')

app = Celery('beauty')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()